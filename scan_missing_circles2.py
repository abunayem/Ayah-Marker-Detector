import sqlite3
import cv2
import numpy as np
import os

conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo_emdadia_perfect.db')
cursor = conn.cursor()

template = cv2.imread('template.png', cv2.IMREAD_GRAYSCALE)
threshold = 0.65 # Higher threshold to avoid false positives!

suspicious_pages = []

print("Scanning pages for missing circles...")
for page in range(1, 611):
    cursor.execute('SELECT COUNT(*) FROM raw_markers WHERE page_number = ?', (page,))
    db_count = cursor.fetchone()[0]
    
    img_path = os.path.join(r'D:\Dev\Temp\EmdadiaPages', f"page{page:03d}.png")
    if not os.path.exists(img_path): continue
    
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    
    # Only search within the main text box! Emdadia text is roughly x in [100, 900], y in [150, 1400]
    h, w = img.shape
    roi_y1 = int(h * 0.1)
    roi_y2 = int(h * 0.95)
    roi_x1 = int(w * 0.1)
    roi_x2 = int(w * 0.9)
    
    roi = img[roi_y1:roi_y2, roi_x1:roi_x2]
    
    res = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
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
    
    # Check if detector found more than the DB
    if detected_count > db_count:
        print(f"Page {page}: DB has {db_count}, but detector found {detected_count}")
        suspicious_pages.append(page)

print("Suspicious Pages (count > db_count):", suspicious_pages)
