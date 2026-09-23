"""
Check known-bad suras by visually inspecting their starting pages.
For each sura that starts on a new page, the first few text lines should be:
  - Line N: Sura header (ornamental, no real ayah text)
  - Line N+1: Bismillah (not an ayah except in Sura 1; Sura 9 has no Bismillah)
  - Line N+2: First ayah text begins

If a circle is detected on the Bismillah line, the sequential assignment will
count it as a real ayah, throwing everything off.

Let's check the starting pages and the cy of the first circle vs the peak positions.
"""
import sqlite3
import cv2
import numpy as np
from scipy.signal import find_peaks

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

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Get all circles ordered by page and cy
c.execute('SELECT id, page_number, cx, cy FROM raw_markers ORDER BY page_number, cy')
all_circles = c.fetchall()

# Group by page
page_circles = {}
for cid, pg, cx, cy in all_circles:
    page_circles.setdefault(pg, []).append((cid, cx, cy))

# For each page that has a sura header, find the text line positions (peaks)
# Then check if any circle falls on the header or Bismillah line

# First, find which pages have sura starts.
# A sura starts on a page when the sequential counter hits the start of a new sura.
# Let's compute this.

sura_start_pages = {}  # sura_number -> page where it starts
circle_idx = 0
current_sura = 1
current_ayah = 1

for cid, pg, cx, cy in all_circles:
    if current_sura not in sura_start_pages:
        sura_start_pages[current_sura] = pg
    
    if current_ayah == hafs_ayat[current_sura - 1]:
        current_sura += 1
        current_ayah = 1
    else:
        current_ayah += 1

print("=== Sura Starting Pages (from sequential assignment) ===")
for s in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 36, 67, 78, 81, 82, 92, 114]:
    if s in sura_start_pages:
        print(f"  Sura {s}: Page {sura_start_pages[s]}")

# Now, for each page where a sura starts mid-page, check if the first circle
# of that sura is actually on the Bismillah line.
print()
print("=== Checking for Bismillah circles ===")
print()

# Get peak positions for each relevant page
def get_peaks(pg):
    import os
    img_path = os.path.join(IMG_DIR, f"page{pg:03d}.png")
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    row_sums = np.sum(thresh, axis=1) / 255
    peaks, _ = find_peaks(row_sums, distance=120, prominence=50)
    valid = [int(p) for p in peaks if 120 <= p <= 2890]
    return valid

# For each sura S, find the page where the PREVIOUS sura ended,
# and check if there's a Bismillah circle.
# We care about cases where a sura starts mid-page (same page where previous sura ended).

# Let's find where each sura ends
sura_end_info = {}  # sura -> (page, cy of last circle)

circle_idx = 0
current_sura = 1
current_ayah = 1

for cid, pg, cx, cy in all_circles:
    if current_ayah == hafs_ayat[current_sura - 1]:
        sura_end_info[current_sura] = (pg, cy, cid)
        current_sura += 1
        current_ayah = 1
    else:
        current_ayah += 1

# Now for each sura transition, check for Bismillah circles
suspicious = []

for sura_num in range(2, 115):
    if sura_num == 9:
        continue  # No Bismillah
    
    prev_sura = sura_num - 1
    if prev_sura not in sura_end_info:
        continue
    
    end_pg, end_cy, end_id = sura_end_info[prev_sura]
    start_pg = sura_start_pages.get(sura_num)
    
    if start_pg is None:
        continue
    
    # Get the first circle of this sura
    first_circle = None
    found_sura = False
    idx = 0
    s = 1; a = 1
    for cid, pg, cx, cy in all_circles:
        if s == sura_num and a == 1 and not found_sura:
            first_circle = (cid, pg, cx, cy)
            found_sura = True
            break
        if a == hafs_ayat[s - 1]:
            s += 1; a = 1
        else:
            a += 1
    
    if first_circle is None:
        continue
    
    fc_id, fc_pg, fc_cx, fc_cy = first_circle
    
    # Now get peaks for this page
    peaks = get_peaks(fc_pg)
    
    if not peaks:
        continue
    
    # Assign the first circle to its nearest peak (line index)
    min_dist = float('inf')
    fc_line = -1
    for i, p in enumerate(peaks):
        d = abs(p - fc_cy)
        if d < min_dist:
            min_dist = d
            fc_line = i
    
    # For suras starting on a new page (different from where previous ended),
    # the header should be near the top. Check if the first text line 
    # (where the first circle is) is line 0 or 1 (which would be the header/bismillah area).
    
    # For suras starting mid-page, check if the first circle is on the expected line.
    
    # Key insight: On pages where a sura starts, the layout is:
    # - Previous sura text (if mid-page start)
    # - Empty/header line (the decorated Sura name box)
    # - Bismillah line
    # - First ayah text line
    
    # If end_pg == start_pg (same page), the gap in cy between end_cy and fc_cy
    # should span at least 2 text lines (header + bismillah).
    # If the gap is only ~1 text line, the first circle might be a Bismillah circle.
    
    if end_pg == fc_pg:
        # Same page transition
        cy_gap = fc_cy - end_cy
        text_line_height = 175  # approximate
        expected_gap = text_line_height * 3  # header + bismillah + half the text lines
        
        if cy_gap < text_line_height * 2.5:
            print(f"  Sura {sura_num}: SAME PAGE ({fc_pg}), end_cy={end_cy}, start_cy={fc_cy}, "
                  f"gap={cy_gap}px ({cy_gap/text_line_height:.1f} lines), "
                  f"line_idx={fc_line}/{len(peaks)-1}")
            suspicious.append((sura_num, fc_id, fc_pg, fc_cx, fc_cy, 'same_page_small_gap'))
    else:
        # Different page transition  
        # The first circle should NOT be on lines 0 or 1 (header/bismillah area)
        if fc_line <= 2:
            # Check: is there a previous sura's circles on this page before this one?
            prev_circles_on_pg = [ci for ci in page_circles.get(fc_pg, []) if ci[2] < fc_cy]
            
            if not prev_circles_on_pg:
                # No previous circles on this page - sura starts at top of page
                # Header is usually line 0-1, Bismillah line 1-2, text starts line 2-3
                print(f"  Sura {sura_num}: NEW PAGE ({fc_pg}), first_cy={fc_cy}, "
                      f"line_idx={fc_line}/{len(peaks)-1}, "
                      f"nearest_peak={peaks[fc_line]}")
                
                if fc_line <= 1:
                    suspicious.append((sura_num, fc_id, fc_pg, fc_cx, fc_cy, 'new_page_too_early'))
            else:
                print(f"  Sura {sura_num}: MID-PAGE ({fc_pg}), first_cy={fc_cy}, "
                      f"line_idx={fc_line}/{len(peaks)-1}, "
                      f"prev_circles_before={len(prev_circles_on_pg)}")

print()
print(f"=== Found {len(suspicious)} suspicious circles ===")
for s, cid, pg, cx, cy, reason in suspicious:
    print(f"  Sura {s}: circle id={cid}, page={pg}, cx={cx}, cy={cy}, reason={reason}")

conn.close()
