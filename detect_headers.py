"""
Definitive approach: Instead of trying to detect Bismillah circles,
check whether the sequential numbering matches known Sura page assignments
from the ACTUAL Emdadia mushaf by visually checking image content.

For each sura start page, check if the page image has a Sura header decoration.
The Sura header is a wide decorative box spanning most of the page width.
We can detect it by looking for lines with very high horizontal ink density.

Then, on pages with Sura headers, count how many circles appear BEFORE the header
(belonging to the previous sura) vs AFTER the header (belonging to the new sura).
The first 1-2 circles after the header should be on the Bismillah/header lines - 
if so, they're false and need to be removed.
"""
import sqlite3
import cv2
import numpy as np
from scipy.signal import find_peaks
import os

DB_PATH = r'D:\Dev\Temp\ayahinfo_emdadia_perfect.db'
IMG_DIR = r'D:\Dev\Temp\EmdadiaPages'

hafs_ayat = [7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111,
             43, 52, 99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77,
             227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75,
             85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55,
             78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52,
             44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25,
             22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
             11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6]

def find_sura_header_line(img_gray):
    """Detect the Sura header decorative box in an image.
    The header has very high ink density spanning most of the page width.
    Returns the y-center of the header line, or None.
    """
    _, thresh = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY_INV)
    h, w = thresh.shape
    
    # Calculate horizontal projection
    row_sums = np.sum(thresh, axis=1) / 255
    
    # The header is a thick decorative band. Look for rows with very high density
    # (>70% of width is ink) spanning at least 100 consecutive rows
    threshold = w * 0.55  # Header rows have >55% of width covered in ink
    
    # Find contiguous blocks of high-density rows
    high_density = row_sums > threshold
    
    headers = []
    in_block = False
    block_start = 0
    for y in range(h):
        if high_density[y]:
            if not in_block:
                block_start = y
                in_block = True
        else:
            if in_block:
                block_height = y - block_start
                if block_height > 80:  # Header is at least 80 pixels tall
                    center = (block_start + y) // 2
                    if 100 < center < h - 100:  # Not at very top/bottom edges
                        headers.append(center)
                in_block = False
    
    return headers

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Scan every page for Sura headers
print("=== Scanning ALL pages for Sura headers ===")
print()

all_pages = sorted(set(pg for pg, in c.execute('SELECT DISTINCT page_number FROM raw_markers')))

bismillah_circles = []

for pg in all_pages:
    img_path = os.path.join(IMG_DIR, f"page{pg:03d}.png")
    if not os.path.exists(img_path):
        continue
    
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    headers = find_sura_header_line(img)
    
    if not headers:
        continue
    
    # This page has a Sura header! Get peaks and circles
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    row_sums = np.sum(thresh, axis=1) / 255
    peaks, _ = find_peaks(row_sums, distance=120, prominence=50)
    valid_peaks = [int(p) for p in peaks if 120 <= p <= 2890]
    
    # Get circles on this page
    c.execute('SELECT id, cx, cy FROM raw_markers WHERE page_number = ? ORDER BY cy', (pg,))
    circles = c.fetchall()
    
    for header_y in headers:
        # The Bismillah line is typically right after the header
        # Find the peak closest to (but after) the header
        header_peak_idx = None
        for i, p in enumerate(valid_peaks):
            if abs(p - header_y) < 100:
                header_peak_idx = i
                break
        
        if header_peak_idx is None:
            # Header might not align with a peak perfectly
            # Find the first peak after the header
            for i, p in enumerate(valid_peaks):
                if p > header_y - 50:
                    header_peak_idx = i
                    break
        
        if header_peak_idx is None:
            continue
        
        # The Bismillah line is the peak right after the header
        bismillah_peak_idx = header_peak_idx + 1
        if bismillah_peak_idx >= len(valid_peaks):
            continue
        
        bismillah_y = valid_peaks[bismillah_peak_idx]
        
        # Check if any circle falls on the header or Bismillah line
        for cid, cx, cy in circles:
            # Circle is on header line
            if abs(cy - valid_peaks[header_peak_idx]) < 90:
                print(f"  Page {pg}: HEADER circle id={cid}, cx={cx}, cy={cy} "
                      f"(header_peak={valid_peaks[header_peak_idx]})")
                bismillah_circles.append(cid)
            # Circle is on Bismillah line
            elif abs(cy - bismillah_y) < 90:
                print(f"  Page {pg}: BISMILLAH circle id={cid}, cx={cx}, cy={cy} "
                      f"(bismillah_peak={bismillah_y})")
                bismillah_circles.append(cid)

print()
print(f"=== Total Bismillah/Header circles found: {len(bismillah_circles)} ===")
for cid in bismillah_circles:
    c.execute('SELECT page_number, cx, cy FROM raw_markers WHERE id = ?', (cid,))
    r = c.fetchone()
    if r:
        print(f"  id={cid}: page={r[0]}, cx={r[1]}, cy={r[2]}")

conn.close()
