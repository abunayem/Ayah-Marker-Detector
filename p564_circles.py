import cv2
import numpy as np

img = cv2.imread(r'D:\Dev\Temp\EmdadiaPages\page564.png', cv2.IMREAD_GRAYSCALE)
h, w = img.shape

import sqlite3
conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo.db')
c = conn.cursor()
c.execute('SELECT line, top_pct, bottom_pct FROM page_lines WHERE page = 564 ORDER BY line')
lines = c.fetchall()

print("Page 564 Hough Circles per line:")
for l, t, b in lines:
    y1 = int(t * h)
    y2 = int(b * h)
    crop = img[y1:y2, :]
    blurred = cv2.medianBlur(crop, 5)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=50, param2=25, minRadius=20, maxRadius=45)
    if circles is not None:
        circs = sorted([c[0] for c in circles[0]], reverse=True)
        circ_str = ", ".join([f"cx={cx:.1f} ({cx/w:.3f})" for cx in circs])
        print(f"Line {l:2d}: {len(circs)} circles -> {circ_str}")
    else:
        print(f"Line {l:2d}: 0 circles")
