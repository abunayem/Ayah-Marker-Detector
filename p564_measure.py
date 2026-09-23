import cv2
import numpy as np

img = cv2.imread(r'D:\Dev\Temp\EmdadiaPages\page564.png', cv2.IMREAD_GRAYSCALE)
h, w = img.shape

# Let's inspect the exact circle centers
# We know the text lines:
import sqlite3
conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo.db')
c = conn.cursor()
c.execute('SELECT line, top_pct, bottom_pct FROM page_lines WHERE page = 564 ORDER BY line')
lines = c.fetchall()

for l, t, b in lines:
    y1 = int(t * h)
    y2 = int(b * h)
    crop = img[y1:y2, :]
    blurred = cv2.medianBlur(crop, 5)
    detected = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=50, param2=25, minRadius=25, maxRadius=42)
    if detected is not None:
        for c_item in detected[0]:
            cx, cy, r = c_item
            print(f"Line {l:2d}: cx={cx:.1f} (pct={cx/w:.3f}), cy={cy:.1f}, r={r:.1f}")
