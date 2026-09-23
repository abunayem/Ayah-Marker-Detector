import sys
import os
import cv2
import numpy as np
import sqlite3
import argparse
from scipy.signal import find_peaks

hafs_ayat = [7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111,
             43, 52, 99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77,
             227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75,
             85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55,
             78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52,
             44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25,
             22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
             11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6]

def find_text_lines(img_gray):
    _, thresh = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY_INV)
    row_sums = np.sum(thresh, axis=1) / 255
    peaks, _ = find_peaks(row_sums, distance=120, prominence=50)
    lines = []
    width = img_gray.shape[1]
    for p in peaks:
        miny = max(0, int(p) - 84)
        maxy = min(img_gray.shape[0], int(p) + 84)
        line_band = thresh[miny:maxy, :]
        col_sums = np.sum(line_band, axis=0)
        non_zero_cols = np.nonzero(col_sums)[0]
        if len(non_zero_cols) > 0:
            minx = non_zero_cols[0]
            maxx = non_zero_cols[-1]
        else:
            minx = 0
            maxx = width
        lines.append(((minx, miny), (maxx, maxy)))
    return lines

def process_page(img_path, param1, param2, min_r, max_r):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None: return [], []
    lines = find_text_lines(img)
    if not lines: return [], []
    global_min_x = min([l[0][0] for l in lines])
    global_max_x = max([l[1][0] for l in lines])
    blurred = cv2.medianBlur(img, 5)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=param1, param2=param2, minRadius=min_r, maxRadius=max_r)
    valid_circles = []
    if circles is not None:
        for c in circles[0]:
            cx, cy, r = c
            if global_min_x - 10 <= cx <= global_max_x + 10:
                valid_circles.append(c)
    line_assigned_circles = {i: [] for i in range(len(lines))}
    for c in valid_circles:
        cx, cy, r = c
        closest_line_idx = 0
        min_dist = float('inf')
        for idx, line in enumerate(lines):
            ly_mid = (line[0][1] + line[1][1]) / 2
            dist = abs(ly_mid - cy)
            if dist < min_dist:
                min_dist = dist
                closest_line_idx = idx
        line_assigned_circles[closest_line_idx].append(c)
    sorted_circles = []
    for idx in range(len(lines)):
        line_circles = sorted(line_assigned_circles[idx], key=lambda c: -c[0])
        for c in line_circles:
            cx, cy, r = c
            sorted_circles.append((idx + 1, cx, cy, r))
    return sorted_circles, lines

def create_db(db_path):
    if os.path.exists(db_path): os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE glyphs (
        glyph_id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_number INTEGER,
        line_number INTEGER,
        sura_number INTEGER,
        ayah_number INTEGER,
        position INTEGER,
        min_x INTEGER,
        max_x INTEGER,
        min_y INTEGER,
        max_y INTEGER
    );
    ''')
    return conn, cursor

def main():
    parser = argparse.ArgumentParser(description="Generate Quran Ayah DB from Mushaf Images using Circle Detection")
    parser.add_argument('--img_dir', type=str, required=True, help='Directory containing page images (e.g., page001.png)')
    parser.add_argument('--out_db', type=str, required=True, help='Output SQLite database file name')
    parser.add_argument('--start_page', type=int, default=1, help='Start page number')
    parser.add_argument('--end_page', type=int, default=611, help='End page number')
    parser.add_argument('--param1', type=int, default=50, help='Hough param1')
    parser.add_argument('--param2', type=int, default=25, help='Hough param2 (lower=more circles)')
    parser.add_argument('--min_r', type=int, default=20, help='Minimum radius of Ayah marker')
    parser.add_argument('--max_r', type=int, default=45, help='Maximum radius of Ayah marker')
    parser.add_argument('--skip_pages', type=str, default='1,2', help='Comma-separated pages to skip (e.g. title pages)')
    parser.add_argument('--start_sura', type=int, default=2, help='The Sura number for the first detected ayah (since skip_pages skips Fatiha)')
    parser.add_argument('--start_ayah', type=int, default=6, help='The Ayah number for the first detected ayah (Baqarah 6 is usually on page 3)')
    
    args = parser.parse_args()
    skip_pages = [int(p) for p in args.skip_pages.split(',') if p]
    conn, cursor = create_db(args.out_db)
    
    sura = args.start_sura
    ayah = args.start_ayah
    total_detected = 0
    insert_data = []
    
    for i in range(args.start_page, args.end_page + 1):
        if i in skip_pages:
            print(f"Skipping page {i} (marked as highly decorated/title page)")
            continue
            
        filename = f"page{i:03d}.png"
        filepath = os.path.join(args.img_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"Warning: {filename} not found.")
            continue
            
        circles, lines = process_page(filepath, args.param1, args.param2, args.min_r, args.max_r)
        
        position = 1
        last_ayah = (0,0)
        
        for c in circles:
            line_num, cx, cy, r = c
            
            if (sura, ayah) != last_ayah:
                position = 1
                last_ayah = (sura, ayah)
            else:
                position += 1
                
            min_x = int(cx - r - 5)
            max_x = int(cx + r + 5)
            min_y = int(cy - r - 5)
            max_y = int(cy + r + 5)
            
            insert_data.append((i, line_num, sura, ayah, position, min_x, max_x, min_y, max_y))
            total_detected += 1
            
            if ayah == hafs_ayat[sura-1]:
                sura += 1
                ayah = 1
            else:
                ayah += 1
                
        print(f"Page {i:03d}: Processed {len(circles)} Ayahs. Next is Sura {sura}, Ayah {ayah}")

    cursor.executemany('''
        INSERT INTO glyphs (page_number, line_number, sura_number, ayah_number, position, min_x, max_x, min_y, max_y)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', insert_data)
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print(f"Database generation complete: {args.out_db}")
    print(f"Total Ayahs detected in processed pages: {total_detected}")
    print(f"Expected remaining Ayahs: {6236 - (12)} (Assuming Fatiha and Baqarah 1-5 are skipped)")
    print("="*50)

if __name__ == "__main__":
    main()
