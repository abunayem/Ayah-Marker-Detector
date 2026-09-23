import sqlite3
import cv2
import numpy as np

conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo_emdadia_perfect.db')
c = conn.cursor()

template = cv2.imread('template.png', cv2.IMREAD_GRAYSCALE)
img = cv2.imread(r'D:\Dev\Temp\EmdadiaPages\page609.png', cv2.IMREAD_GRAYSCALE)

c.execute('SELECT COUNT(*) FROM raw_markers WHERE page_number = 609')
db_count = c.fetchone()[0]

res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
loc = np.where(res >= 0.65)
points = []
for pt in zip(*loc[::-1]):
    matched = False
    for p in points:
        if abs(p[0] - pt[0]) < 20 and abs(p[1] - pt[1]) < 20:
            matched = True
            break
    if not matched:
        points.append(pt)
        
print(f"DB count: {db_count}, Detected count: {len(points)}")
