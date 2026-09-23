import sqlite3
import cv2
import numpy as np
import os

conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo_emdadia_perfect.db')
cursor = conn.cursor()

template = cv2.imread('template.png', cv2.IMREAD_GRAYSCALE)
threshold = 0.55

suspicious_pages = []

print("Scanning pages for missing circles...")
for page in range(1, 611):
    cursor.execute('SELECT COUNT(*) FROM raw_markers WHERE page_number = ?', (page,))
    db_count = cursor.fetchone()[0]
    
    img_path = os.path.join(r'D:\Dev\Temp\EmdadiaPages', f"page{page:03d}.png")
    if not os.path.exists(img_path): continue
    
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    
    points = []
    for pt in zip(*loc[::-1]):
        matched = False
        for p in points:
            if abs(p[0] - pt[0]) < 20 and abs(p[1] - pt[1]) < 20:
                matched = True
                break
        if not matched:
            points.append(pt)
            
    detected_count = len(points)
    
    # If template matcher finds MORE circles than what's in the DB, it might be a missing circle!
    if detected_count > db_count + 1: # +1 tolerance for false positive in template matcher
        print(f"Page {page}: DB has {db_count}, but detector found ~{detected_count}")
        suspicious_pages.append(page)

print("Suspicious Pages:", suspicious_pages)
