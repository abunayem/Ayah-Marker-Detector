import sqlite3
import cv2
import os

conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo_emdadia_perfect.db')
c = conn.cursor()
c.execute('SELECT cx, cy FROM raw_markers WHERE page_number = 609 LIMIT 1')
cx, cy = c.fetchone()
conn.close()

img = cv2.imread(r'D:\Dev\Temp\EmdadiaPages\page609.png', cv2.IMREAD_GRAYSCALE)
r = 25 # radius of template
template = img[cy-r:cy+r, cx-r:cx+r]
cv2.imwrite('template.png', template)
print("Template saved!")
