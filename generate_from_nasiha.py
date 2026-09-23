import sqlite3
import cv2
import numpy as np
import os
from scipy.signal import find_peaks

def find_robust_lines(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None: return []
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    row_sums = np.sum(thresh, axis=1) / 255
    peaks, _ = find_peaks(row_sums, distance=120, prominence=50)
    lines = []
    for p in peaks:
        miny = max(0, int(p) - 84) # 168/2
        maxy = min(img.shape[0], int(p) + 84)
        lines.append((miny, maxy))
    return lines

def main():
    conn_src = sqlite3.connect(r'D:\Dev\Temp\db\nasiha_v2.db')
    cursor_src = conn_src.cursor()
    
    if os.path.exists('ayahinfo_nasiha.db'):
        os.remove('ayahinfo_nasiha.db')
    conn_dest = sqlite3.connect('ayahinfo_nasiha.db')
    cursor_dest = conn_dest.cursor()
    
    cursor_dest.execute('''
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
    
    cursor_src.execute("SELECT page, sura, ayah, line, left, right FROM ayah_highlights ORDER BY page, sura, ayah, line")
    rows = cursor_src.fetchall()
    
    current_page = -1
    page_lines = []
    width = 1859
    
    # We need to map the 'line' from nasiha (0 to 14) to the detected lines on the image.
    # Typically, the image has 16 or 17 lines (header + 15 text lines + footer).
    # If the text has 15 lines, the header is usually line 0, text is 1-15.
    # Nasiha 'line' is 0 to 14. So Nasiha line X corresponds to detected line X + offset.
    
    # We will write a simple heuristic: the last Nasiha line corresponds to the last or 2nd to last detected line.
    
    insert_data = []
    position_counter = 1
    last_ayah = (0,0)
    
    for row in rows:
        page, sura, ayah, line, left_pct, right_pct = row
        
        if page != current_page:
            current_page = page
            print(f"Processing page {page}...")
            img_path = f'D:\\Dev\\Temp\\EmdadiaPages\\page{page:03d}.png'
            page_lines = find_robust_lines(img_path)
            
        if not page_lines: continue
        
        # Nasiha lines are 0-indexed up to 14.
        # Images have ~17 detected lines. Usually 1 header, 15 text, 1 footer.
        # So text lines are index 1 to 15. Thus detected_line_idx = line + 1.
        detected_idx = line + 1
        if detected_idx >= len(page_lines):
            detected_idx = len(page_lines) - 1
            
        min_y, max_y = page_lines[detected_idx]
        
        # Invert left/right if it's RTL? Nasiha 'left' and 'right' are probably absolute from left edge.
        # left_pct is fraction from left.
        # wait, left_pct in nasiha is like 0.74, right_pct is 0.82 for the first word!
        # Arabic is RTL, so the first word should have high X coordinates.
        # This matches: 0.74 to 0.82 is on the right side of the page!
        min_x = int(left_pct * width)
        max_x = int(right_pct * width)
        
        if (sura, ayah) != last_ayah:
            position_counter = 1
            last_ayah = (sura, ayah)
        else:
            position_counter += 1
            
        insert_data.append((page, detected_idx, sura, ayah, position_counter, min_x, max_x, min_y, max_y))
        
    cursor_dest.executemany(
        "INSERT INTO glyphs (page_number, line_number, sura_number, ayah_number, position, min_x, max_x, min_y, max_y) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        insert_data
    )
    
    conn_dest.commit()
    conn_dest.close()
    conn_src.close()
    print("Successfully generated ayahinfo_nasiha.db")

if __name__ == '__main__':
    main()
