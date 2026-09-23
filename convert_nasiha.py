import sqlite3
import cv2
import numpy as np
import os
from scipy.signal import find_peaks

def find_robust_lines(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None: return [], 0
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    row_sums = np.sum(thresh, axis=1) / 255
    peaks, _ = find_peaks(row_sums, distance=120, prominence=50)
    lines = []
    for p in peaks:
        miny = max(0, int(p) - 84)
        maxy = min(img.shape[0], int(p) + 84)
        lines.append((miny, maxy))
    return lines, img.shape[1]

def main():
    conn_src = sqlite3.connect(r'D:\Dev\Temp\db\nasiha_v2.db')
    cursor_src = conn_src.cursor()
    
    if os.path.exists('ayahinfo_perfect.db'):
        os.remove('ayahinfo_perfect.db')
    conn_dest = sqlite3.connect('ayahinfo_perfect.db')
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
    lines = []
    width = 1859
    
    for row in rows:
        page, sura, ayah, line, left_pct, right_pct = row
        
        if page != current_page:
            current_page = page
            print(f"Processing page {page}...")
            img_path = f'D:\\Dev\\Temp\\EmdadiaPages\\page{page:03d}.png'
            lines, w = find_robust_lines(img_path)
            if w > 0: width = w
            
        # Nasiha DB line index might be 1-based, or it might correspond directly to our peaks
        # Let's assume line is 1-based index (1 to 15, sometimes more if header/footer).
        # We need to map the DB line number to the actual line Y bounds.
        # This mapping can be tricky because 
asiha_v2.db line numbers might not include header/footer.
        # We will handle it based on how many lines nasiha specifies vs what we detect.
        
        # For now, let's just write a stub and we'll check how Nasiha handles line numbers!
        pass
    
if __name__ == '__main__':
    pass
