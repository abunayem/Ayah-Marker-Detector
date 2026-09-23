import sqlite3
import cv2
import numpy as np
import os
import argparse
from scipy.signal import find_peaks

def find_text_lines(img_gray):
    # Find text lines using horizontal projection
    _, thresh = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY_INV)
    row_sums = np.sum(thresh, axis=1) / 255
    peaks, _ = find_peaks(row_sums, distance=120, prominence=50)
    
    # Filter to only the actual text separators (exclude outer decorative borders)
    valid_peaks = [p for p in peaks if 120 <= p <= 2890]
    
    lines = []
    width = img_gray.shape[1]
    
    # Text lines are between the peaks!
    for i in range(len(valid_peaks) - 1):
        miny = int(valid_peaks[i])
        maxy = int(valid_peaks[i+1])
        
        # To find minx and maxx, we look at the pixels between miny and maxy
        line_band = thresh[miny:maxy, :]
        col_sums = np.sum(line_band, axis=0)
        non_zero_cols = np.nonzero(col_sums)[0]
        if len(non_zero_cols) > 0:
            minx = non_zero_cols[0]
            maxx = non_zero_cols[-1]
        else:
            minx = 0; maxx = width
            
        lines.append(((minx, miny), (maxx, maxy)))
        
    return lines


def compile_db(raw_db_path, out_db_path, img_dir):
    conn_in = sqlite3.connect(raw_db_path)
    cursor_in = conn_in.cursor()
    cursor_in.execute('SELECT page_number, sura_number, ayah_number, cx, cy FROM raw_markers ORDER BY page_number, sura_number, ayah_number')
    markers = cursor_in.fetchall()
    
    if os.path.exists(out_db_path):
        os.remove(out_db_path)
        
    conn_out = sqlite3.connect(out_db_path)
    cursor_out = conn_out.cursor()
    cursor_out.execute('''
    CREATE TABLE ayah_highlights (
        ayah_id INTEGER PRIMARY KEY AUTOINCREMENT,
        page INTEGER,
        sura INTEGER,
        ayah INTEGER,
        line INTEGER,
        "left" REAL,
        "right" REAL
    )
    ''')
    
    cursor_out.execute('''
    CREATE TABLE page_lines (
        page INTEGER,
        line INTEGER,
        top_pct REAL,
        bottom_pct REAL
    )
    ''')
    
    all_lines = []
    for pg in range(1, 612):
        img_path = os.path.join(img_dir, f"page{pg:03d}.png")
        if not os.path.exists(img_path): continue
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        width = img.shape[1]
        
        # For pages 1 and 2, horizontal projection fails due to massive decorative borders
        if pg == 1 or pg == 2:
            if pg == 1:
                baselines = [1341, 1506, 1684, 1853, 2036, 2214, 2390, 2566]
            else:
                baselines = [1151, 1326, 1501, 1676, 1851, 2026, 2201, 2376, 2551]
                
            lines = []
            for p in baselines:
                lines.append(((0, p - 85), (width, p + 85)))
        else:
            lines = find_text_lines(img)
            
        if not lines: continue
        
        global_min_x = min([l[0][0] for l in lines])
        global_max_x = max([l[1][0] for l in lines])
        
        for idx, line in enumerate(lines):
            cursor_out.execute('''
                INSERT INTO page_lines (page, line, top_pct, bottom_pct)
                VALUES (?, ?, ?, ?)
            ''', (pg, idx + 1, line[0][1] / float(img.shape[0]), line[1][1] / float(img.shape[0])))
            
            all_lines.append({
                'page': pg,
                'line_idx': idx + 1,
                'bbox': line,
                'width': width,
                'global_min_x': global_min_x,
                'global_max_x': global_max_x,
                'circles': []
            })
            
    # Assign markers to lines
    for m in markers:
        pg, sura, ayah, cx, cy = m
        best_line = None
        min_dist = float('inf')
        for line in all_lines:
            if line['page'] != pg: continue
            ly_mid = (line['bbox'][0][1] + line['bbox'][1][1]) / 2
            dist = abs(ly_mid - cy)
            if dist < min_dist:
                min_dist = dist
                best_line = line
        if best_line:
            best_line['circles'].append(m)
            
    # Sort circles right-to-left
    for line in all_lines:
        line['circles'].sort(key=lambda c: -c[3])
        
    # Generate segments
    last_seen_sura = 1
    transition_skips = 0
    for i, line in enumerate(all_lines):
        current_right_x = line['global_max_x']
        
        for m in line['circles']:
            pg, sura, ayah, cx, cy = m
            left_pct = cx / float(line['width'])
            right_pct = current_right_x / float(line['width'])
            cursor_out.execute('''
                INSERT INTO ayah_highlights (page, sura, ayah, line, "left", "right")
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (pg, sura, ayah, line['line_idx'], left_pct, right_pct))
            current_right_x = cx
            last_seen_sura = sura
            transition_skips = 0

            
        # Remainder of line belongs to next ayah
        next_m = None
        for future_line in all_lines[i+1:]:
            if len(future_line['circles']) > 0:
                next_m = future_line['circles'][0]
                break
        
        if next_m:
            _, n_sura, n_ayah, _, _ = next_m
            
            # Handle skipping Sura Header (and Bismillah) lines
            if n_sura != last_seen_sura:
                # If this is a completely empty line before the first circle of the new Sura
                if len(line['circles']) == 0:
                    transition_skips += 1
                    required_skips = 1 if n_sura == 9 else 2
                    
                    # If we've skipped the required header lines, the remaining empty lines
                    # actually belong to the text of the first Ayah!
                    if transition_skips > required_skips:
                        last_seen_sura = n_sura

            # ONLY highlight the remainder of the line if it belongs to the SAME Sura!
            if n_sura == last_seen_sura:
                left_pct = line['global_min_x'] / float(line['width'])
                right_pct = current_right_x / float(line['width'])
                if current_right_x - line['global_min_x'] > 20: # only if significant width remains
                    cursor_out.execute('''
                        INSERT INTO ayah_highlights (page, sura, ayah, line, "left", "right")
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (line['page'], n_sura, n_ayah, line['line_idx'], left_pct, right_pct))

    conn_out.commit()
    conn_out.close()
    print("Successfully compiled into ayah_highlights format!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_db', type=str, required=True)
    parser.add_argument('--out_db', type=str, required=True)
    parser.add_argument('--img_dir', type=str, required=True)
    args = parser.parse_args()
    compile_db(args.raw_db, args.out_db, args.img_dir)
