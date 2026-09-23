import cv2
import sqlite3

img = cv2.imread(r'D:\Dev\Temp\EmdadiaPages\page590.png')
h, w, _ = img.shape

conn = sqlite3.connect(r'D:\Dev\Temp\Backup\ayahinfo.db')
c = conn.cursor()
c.execute('SELECT line, top_pct, bottom_pct FROM page_lines WHERE page = 590 ORDER BY line')
lines = c.fetchall()

for l, t, b in lines:
    if 9 <= l <= 15:
        y1 = int(t * h)
        y2 = int(b * h)
        crop = img[y1:y2, :]
        cv2.imwrite(f'crop_p590_line{l}.png', crop)
        print(f"Saved Line {l:2d}: y={y1} to {y2}")
