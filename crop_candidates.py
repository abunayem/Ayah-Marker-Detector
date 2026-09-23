import cv2
import sqlite3
import os

conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo.db')
c = conn.cursor()

mid_page_suras = [
    (14, 255, 7),
    (16, 267, 9),
    (35, 434, 10),
    (49, 515, 9),
    (62, 553, 7),
    (63, 554, 12),
    (68, 564, 12),
    (71, 571, 14),
]

for sura, pg, test_line in mid_page_suras:
    img_path = rf'D:\Dev\Temp\EmdadiaPages\page{pg:03d}.png'
    if not os.path.exists(img_path):
        continue
    img = cv2.imread(img_path)
    h, w, _ = img.shape
    
    # Get lines around test_line
    c.execute('SELECT line, top_pct, bottom_pct FROM page_lines WHERE page = ? AND line BETWEEN ? AND ?', (pg, test_line - 2, test_line + 1))
    lines = c.fetchall()
    
    for l, t, b in lines:
        y1 = int(t * h)
        y2 = int(b * h)
        crop = img[y1:y2, :]
        out_name = f'crop_check_s{sura}_p{pg}_l{l}.png'
        cv2.imwrite(out_name, crop)
        print(f"Saved Sura {sura} Page {pg} Line {l}: {out_name}")
