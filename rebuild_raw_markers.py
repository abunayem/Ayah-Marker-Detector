"""
REBUILD raw_markers using the SAME filtering as the original generate_imdadia_db.py:
- Use actual text line boundaries for filtering (not hardcoded margins)
- Skip pages 1 and 2 (handle separately - they have special decorative layouts)
- Filter circles that land on non-text lines (Sura headers, Bismillahs)

Key insight: we can detect Sura header/Bismillah lines because they have
NO circles from the original detection. We identify these by checking
the density pattern: lines with very high density (>0.5) are horizontal
separators. Between two consecutive separators, if the text density is
characteristic of a header (high ornamental density) or Bismillah, we skip it.

SIMPLER APPROACH: Use the text line peak count. Standard pages have exactly
15 text lines (peaks). Pages with Sura headers have 16 peaks (the extra peak
is the Bismillah or header). We can identify which peaks are text vs header
by checking what's around them.

SIMPLEST APPROACH: For each page, detect circles using the ORIGINAL method
(text bounds filtering). Then check if the total count is reasonable.
The original script's output log should tell us exactly how many circles
were on each page.
"""
import cv2
import numpy as np
import sqlite3
import os
from scipy.signal import find_peaks

IMG_DIR = r'D:\Dev\Temp\EmdadiaPages'
DB_PATH = r'D:\Dev\Temp\ayahinfo_emdadia_perfect.db'

hafs_ayat = [7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111,
             43, 52, 99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77,
             227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75,
             85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55,
             78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52,
             44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25,
             22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
             11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6]

TOTAL_AYAHS = sum(hafs_ayat)

def find_text_lines(img_gray):
    """Exact copy of original generate_imdadia_db.py line detection."""
    _, thresh = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY_INV)
    row_sums = np.sum(thresh, axis=1) / 255
    peaks, _ = find_peaks(row_sums, distance=120, prominence=50)
    lines = []
    width = img_gray.shape[1]
    for p in peaks:
        if not (120 <= p <= 2890):
            continue
        miny = max(0, int(p) - 84)
        maxy = min(img_gray.shape[0], int(p) + 84)
        line_band = thresh[miny:maxy, :]
        col_sums = np.sum(line_band, axis=0)
        non_zero_cols = np.nonzero(col_sums)[0]
        if len(non_zero_cols) > 0:
            minx = non_zero_cols[0]
            maxx = non_zero_cols[-1]
        else:
            minx = 0
            maxx = width
        lines.append({
            'peak': int(p),
            'miny': miny,
            'maxy': maxy,
            'minx': int(minx),
            'maxx': int(maxx)
        })
    return lines

def detect_page_circles(img_gray, lines):
    """Detect circles with ORIGINAL text bounds filtering."""
    if not lines:
        return []
    
    global_min_x = min(l['minx'] for l in lines)
    global_max_x = max(l['maxx'] for l in lines)
    
    blurred = cv2.medianBlur(img_gray, 5)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=50, param2=25, minRadius=20, maxRadius=45)
    
    valid = []
    if circles is not None:
        for c in circles[0]:
            cx, cy, r = c
            if global_min_x - 10 <= cx <= global_max_x + 10:
                valid.append((int(cx), int(cy)))
    
    return valid

def assign_to_nearest_line(circles, lines):
    """Assign circles to nearest line and sort in reading order (RTL per line)."""
    line_map = {i: [] for i in range(len(lines))}
    
    for cx, cy in circles:
        best = 0
        best_dist = float('inf')
        for i, l in enumerate(lines):
            d = abs(cy - l['peak'])
            if d < best_dist:
                best_dist = d
                best = i
        line_map[best].append((cx, cy))
    
    # Sort RTL within each line, then concatenate
    ordered = []
    for i in range(len(lines)):
        sorted_line = sorted(line_map[i], key=lambda c: -c[0])
        ordered.extend(sorted_line)
    
    return ordered

# ========== REBUILD ==========
print("=== Rebuilding raw_markers database ===")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS raw_markers')
cursor.execute('''CREATE TABLE raw_markers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_number INTEGER,
    sura_number INTEGER,
    ayah_number INTEGER,
    cx INTEGER,
    cy INTEGER
)''')
conn.commit()

# Phase 1: Detect and insert circles for pages 3-611
# (Skip pages 1 and 2 - special decorative pages handled separately)
total = 0
page_counts = {}

for pg in range(3, 612):
    img_path = os.path.join(IMG_DIR, f"page{pg:03d}.png")
    if not os.path.exists(img_path):
        continue
    
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    lines = find_text_lines(img)
    circles = detect_page_circles(img, lines)
    ordered = assign_to_nearest_line(circles, lines)
    
    for cx, cy in ordered:
        cursor.execute('INSERT INTO raw_markers (page_number, sura_number, ayah_number, cx, cy) VALUES (?, 0, 0, ?, ?)',
                       (pg, cx, cy))
        total += 1
    
    page_counts[pg] = len(ordered)
    
    if pg % 100 == 0:
        print(f"  Processed page {pg}: {len(ordered)} circles")

conn.commit()

# Phase 2: Handle pages 1 and 2 specially
# Page 1: Al-Fatiha - 7 ayahs, peaks at known positions
# Page 2: Al-Baqarah starts - first 5 ayahs

# For page 1, the known text peaks are:
p1_peaks = [1341, 1506, 1684, 1853, 2036, 2214, 2390, 2566]
img1 = cv2.imread(os.path.join(IMG_DIR, "page001.png"), cv2.IMREAD_GRAYSCALE)
blurred1 = cv2.medianBlur(img1, 5)
c1 = cv2.HoughCircles(blurred1, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                       param1=50, param2=25, minRadius=20, maxRadius=45)
p1_circles = []
if c1 is not None:
    for c in c1[0]:
        cx, cy, r = c
        if 150 <= cx <= 1500 and 1200 <= cy <= 2700:
            p1_circles.append((int(cx), int(cy)))

# Assign to lines by nearest peak
p1_ordered = []
for peak in p1_peaks:
    line_c = [(cx, cy) for cx, cy in p1_circles if abs(cy - peak) < 90]
    line_c.sort(key=lambda c: -c[0])
    p1_ordered.extend(line_c)

for cx, cy in p1_ordered:
    cursor.execute('INSERT INTO raw_markers (page_number, sura_number, ayah_number, cx, cy) VALUES (1, 0, 0, ?, ?)',
                   (cx, cy))
    total += 1
page_counts[1] = len(p1_ordered)

# For page 2
p2_peaks = [1151, 1326, 1501, 1676, 1851, 2026, 2201, 2376, 2551]
img2 = cv2.imread(os.path.join(IMG_DIR, "page002.png"), cv2.IMREAD_GRAYSCALE)
blurred2 = cv2.medianBlur(img2, 5)
c2 = cv2.HoughCircles(blurred2, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                       param1=50, param2=25, minRadius=20, maxRadius=45)
p2_circles = []
if c2 is not None:
    for c in c2[0]:
        cx, cy, r = c
        if 150 <= cx <= 1500 and 1000 <= cy <= 2700:
            p2_circles.append((int(cx), int(cy)))

p2_ordered = []
for peak in p2_peaks:
    line_c = [(cx, cy) for cx, cy in p2_circles if abs(cy - peak) < 90]
    line_c.sort(key=lambda c: -c[0])
    p2_ordered.extend(line_c)

for cx, cy in p2_ordered:
    cursor.execute('INSERT INTO raw_markers (page_number, sura_number, ayah_number, cx, cy) VALUES (2, 0, 0, ?, ?)',
                   (cx, cy))
    total += 1
page_counts[2] = len(p2_ordered)

conn.commit()

print(f"\nTotal circles detected: {total}")
print(f"Expected: {TOTAL_AYAHS}")
print(f"Difference: {total - TOTAL_AYAHS}")
print(f"Page 1: {page_counts.get(1, 0)} circles")
print(f"Page 2: {page_counts.get(2, 0)} circles")

# Show pages with most circles for debugging
print("\nPages with >20 circles (suspicious):")
for pg in sorted(page_counts.keys()):
    if page_counts[pg] > 20:
        print(f"  Page {pg}: {page_counts[pg]} circles")

# Phase 3: Assign sura/ayah numbers
print("\n=== Assigning sura/ayah numbers ===")
cursor.execute('SELECT id, page_number, cx, cy FROM raw_markers ORDER BY page_number, id')
all_circles = cursor.fetchall()

sura = 1
ayah = 1
updates = []
assigned = 0

for cid, pg, cx, cy in all_circles:
    if sura > 114:
        break
    updates.append((sura, ayah, cid))
    assigned += 1
    if ayah == hafs_ayat[sura - 1]:
        sura += 1
        ayah = 1
    else:
        ayah += 1

print(f"Assigned {assigned} of {total} circles")
if assigned < total:
    print(f"  {total - assigned} extra circles left unassigned (false positives)")

cursor.executemany('UPDATE raw_markers SET sura_number = ?, ayah_number = ? WHERE id = ?', updates)
conn.commit()

# Verification
print("\n=== Verification ===")
for s in [1, 2, 36, 74, 81, 82, 88, 92, 98, 100, 104, 105, 107, 108, 114]:
    cursor.execute('SELECT page_number, cx, cy FROM raw_markers WHERE sura_number = ? AND ayah_number = 1', (s,))
    r = cursor.fetchone()
    if r:
        print(f"  Sura {s:3d}: page={r[0]}, cx={r[1]}, cy={r[2]}")
    else:
        print(f"  Sura {s:3d}: NOT FOUND!")

conn.close()
print("\nDone!")
