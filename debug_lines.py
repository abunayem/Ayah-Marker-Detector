"""
CORRECT APPROACH: Use the KNOWN TOTAL AYAH COUNT as a constraint.

The total number of real ayah markers = 6236 (sum of all ayahs).
The database has exactly 6236 circles. 
This means: EITHER all circles are real (no Bismillah circles) and the 
numbering is just wrong due to line grouping issues, OR some circles are 
Bismillah but the same number of real circles were missed.

Given that the total is EXACTLY 6236, it's most likely that ALL circles 
are real ayah markers and NONE are Bismillah circles. The only issue is 
how they're grouped into lines and sorted RTL.

The real problem: the line grouping threshold of 80px is either too loose 
or too tight, causing some circles from different lines to be merged 
(scrambling the RTL sort order) or circles from the same line to be split.

Let's verify by checking a known problematic page (page 590) in detail.
"""
import sqlite3

DB_PATH = r'D:\Dev\Temp\ayahinfo_emdadia_perfect.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Page 590: Sura 80/81 transition
c.execute('SELECT id, cx, cy FROM raw_markers WHERE page_number = 590 ORDER BY cy')
circles = c.fetchall()
print("=== Page 590 circles ===")
for cid, cx, cy in circles:
    print(f"  id={cid}, cx={cx:4d}, cy={cy}")

# Let's see the EXPECTED assignment for this page
# Sura 80 (Abasa) has 42 ayahs. Looking at the page, it should have 
# the last few ayahs of Sura 80 and first few of Sura 81.

# Also check page 601 (Sura 91/92 transition)  
print()
print("=== Page 601 circles ===")
c.execute('SELECT id, cx, cy FROM raw_markers WHERE page_number = 601 ORDER BY cy')
circles = c.fetchall()
for cid, cx, cy in circles:
    print(f"  id={cid}, cx={cx:4d}, cy={cy}")

# Check what peak positions are
import cv2
import numpy as np
from scipy.signal import find_peaks
import os

for pg in [590, 601]:
    img = cv2.imread(os.path.join(r'D:\Dev\Temp\EmdadiaPages', f'page{pg:03d}.png'), cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    row_sums = np.sum(thresh, axis=1) / 255
    peaks, _ = find_peaks(row_sums, distance=120, prominence=50)
    valid = [int(p) for p in peaks if 120 <= p <= 2890]
    
    print(f"\n=== Page {pg} peaks ===")
    for i, p in enumerate(valid):
        print(f"  Line {i}: peak={p}")
    
    # Now assign circles to lines
    c.execute('SELECT id, cx, cy FROM raw_markers WHERE page_number = ? ORDER BY cy', (pg,))
    circles = c.fetchall()
    
    print(f"\n=== Page {pg} circles grouped by line ===")
    for i, p in enumerate(valid):
        lo = (valid[i-1] + p) // 2 if i > 0 else 0
        hi = (p + valid[i+1]) // 2 if i < len(valid)-1 else 3000
        line_circles = [(cid, cx, cy) for cid, cx, cy in circles if lo <= cy < hi]
        if line_circles:
            sorted_rtl = sorted(line_circles, key=lambda x: -x[1])
            labels = [f"cx={cx}" for _, cx, cy in sorted_rtl]
            print(f"  Line {i} (peak={p}): {len(line_circles)} circles -> {', '.join(labels)}")
        else:
            print(f"  Line {i} (peak={p}): empty")

conn.close()
