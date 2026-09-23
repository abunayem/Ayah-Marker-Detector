import sqlite3
import cv2
import numpy as np
import os
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
            minx = 0; maxx = width
        lines.append(((minx, miny), (maxx, maxy)))
    return lines

conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo_emdadia_perfect.db')
cursor = conn.cursor()

# Get all raw markers grouped by page
cursor.execute('SELECT id, page_number, cx, cy FROM raw_markers ORDER BY page_number')
all_markers = cursor.fetchall()

page_markers = {}
for m in all_markers:
    pg = m[1]
    if pg not in page_markers:
        page_markers[pg] = []
    page_markers[pg].append(m)

# Emdadia starts at Sura 1, Ayah 1 on Page 1
current_sura = 1
current_ayah = 1

updates = []

for pg in sorted(page_markers.keys()):
    img_path = os.path.join(r'D:\Dev\Temp\EmdadiaPages', f"page{pg:03d}.png")
    if not os.path.exists(img_path): continue
    
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    lines = find_text_lines(img)
    if not lines: continue
    
    p_markers = page_markers[pg]
    
    line_assigned = {i: [] for i in range(len(lines))}
    for m in p_markers:
        cy = m[3]
        closest_idx = 0
        min_dist = float('inf')
        for idx, line in enumerate(lines):
            ly_mid = (line[0][1] + line[1][1]) / 2
            dist = abs(ly_mid - cy)
            if dist < min_dist:
                min_dist = dist
                closest_idx = idx
        line_assigned[closest_idx].append(m)
        
    for idx in range(len(lines)):
        line_circles = sorted(line_assigned[idx], key=lambda c: -c[2]) # RTL
        
        for m in line_circles:
            marker_id = m[0]
            
            updates.append((current_sura, current_ayah, marker_id))
            
            if current_ayah == hafs_ayat[current_sura - 1]:
                current_sura += 1
                current_ayah = 1
            else:
                current_ayah += 1

cursor.executemany('''
    UPDATE raw_markers 
    SET sura_number = ?, ayah_number = ?
    WHERE id = ?
''', updates)

conn.commit()
conn.close()
print("Successfully recalculated all Sura and Ayah numbers based on coordinates!")
