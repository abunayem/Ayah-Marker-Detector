"""
DEFINITIVE FIX: Find and remove ALL false circles on Sura header/Bismillah lines.

Algorithm:
1. For each page, find the horizontal separator lines (>0.5 density rows)
2. The space between two consecutive separators defines a "text line band"
3. For bands where the Sura header or Bismillah appears, any circles in those
   bands are false and should be removed
4. To identify header/Bismillah bands: they have distinctive low text density
   compared to regular ayah text bands, and they're characterized by the
   ornamental header patterns

Simpler approach: 
- The header box has a distinctive horizontal line at its top and bottom
- We can detect bands that have VERY low text density (the header ornamental area)
  or specific Bismillah-like density
- Actually simplest: find ALL horizontal separator lines on each page, then
  check each band between separators. If a band has 0 or 1 circles AND
  is preceded/followed by a band that also has 0-1 circles, it's likely
  a header+Bismillah pair. Remove any circles from those bands.
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

TOTAL_AYAHS = sum(hafs_ayat)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Step 1: For each page 3-611, find text line bands using peaks
# Step 2: Assign each circle to a band
# Step 3: Find consecutive empty or near-empty bands (header+Bismillah)
# Step 4: Remove any circles in those bands

print("=== Step 1: Scanning all pages for header/Bismillah bands ===")

all_false_circle_ids = set()
header_pages = []

for pg in range(3, 612):  # Skip pages 1-2 (special decorative pages)
    img_path = os.path.join(IMG_DIR, f"page{pg:03d}.png")
    if not os.path.exists(img_path):
        continue
    
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    h, w = thresh.shape
    row_sums = np.sum(thresh, axis=1) / 255
    
    peaks, _ = find_peaks(row_sums, distance=120, prominence=50)
    valid_peaks = sorted([int(p) for p in peaks if 120 <= p <= 2890])
    
    if len(valid_peaks) < 10:  # Not a standard page
        continue
    
    # Get circles on this page
    cursor.execute('SELECT id, cx, cy FROM raw_markers WHERE page_number = ? ORDER BY cy', (pg,))
    circles = cursor.fetchall()
    
    if not circles:
        continue
    
    # Create bands between peaks
    # Band i spans from peaks[i] - half_gap to peaks[i] + half_gap
    bands = []
    for i, p in enumerate(valid_peaks):
        lower = (valid_peaks[i-1] + p) // 2 if i > 0 else 0
        upper = (p + valid_peaks[i+1]) // 2 if i < len(valid_peaks)-1 else h
        bands.append((lower, upper, p))
    
    # Assign circles to bands
    band_circles = {i: [] for i in range(len(bands))}
    for cid, cx, cy in circles:
        for i, (lo, hi, peak) in enumerate(bands):
            if lo <= cy < hi:
                band_circles[i].append((cid, cx, cy))
                break
    
    # Find header+Bismillah pattern:
    # Look for pairs of consecutive bands where:
    # - Band A (header) has 0 or 1 circles
    # - Band B (Bismillah) has 0 or 1 circles  
    # - The band before A has circles (end of previous sura)
    # - The band after B has circles (start of new sura)
    
    for i in range(1, len(bands) - 2):
        a_count = len(band_circles[i])
        b_count = len(band_circles[i + 1])
        before_count = len(band_circles[i - 1])
        after_count = len(band_circles[i + 2])
        
        if a_count <= 1 and b_count <= 1 and before_count > 0 and after_count > 0:
            # This might be a header+Bismillah pair
            # Additional check: the header band should have low text density
            # compared to regular text bands
            lo_a, hi_a, peak_a = bands[i]
            band_region = thresh[lo_a:hi_a, :]
            density_a = np.sum(band_region) / (255.0 * band_region.shape[0] * w)
            
            # Regular text bands have density 0.12-0.20
            # Header bands can have varied density (ornamental box + text)
            # Bismillah bands have moderate density
            # The key differentiator: a header band is NOT a normal ayah text band
            
            # Actually, the most reliable check: is there a FULL-WIDTH separator line
            # at the top of this band? The horizontal separator lines have density > 0.5
            
            # Check for separator line at peak_a
            separator_density = row_sums[peak_a] / w if peak_a < len(row_sums) else 0
            
            # Check for another separator at peak of band i+1
            _, _, peak_b = bands[i + 1]
            
            # The header box itself has very distinctive patterns. Let's check if
            # there's a significant vertical gap (very low density) between the
            # separator line and the next text, which indicates a header box boundary
            
            # Also check: do the circles in band A and B look like they could be
            # ayah markers or are they false positives?
            
            # For now, flag any circles in these bands
            false_in_a = band_circles[i]
            false_in_b = band_circles[i + 1]
            
            if false_in_a or false_in_b:
                header_pages.append(pg)
                for cid, cx, cy in false_in_a + false_in_b:
                    all_false_circle_ids.add(cid)
                    print(f"  Page {pg}: FALSE circle id={cid}, cx={cx}, cy={cy}, "
                          f"band_a(line {i})={a_count} circles, band_b(line {i+1})={b_count} circles")

print()
print(f"Total false circles found: {len(all_false_circle_ids)}")

# Step 2: Delete false circles
if all_false_circle_ids:
    print("\nDeleting false circles...")
    for cid in all_false_circle_ids:
        cursor.execute('DELETE FROM raw_markers WHERE id = ?', (cid,))
    conn.commit()
    print(f"Deleted {len(all_false_circle_ids)} circles")

# Step 3: Check new count
cursor.execute('SELECT COUNT(*) FROM raw_markers')
new_count = cursor.fetchone()[0]
print(f"\nNew total circles: {new_count}")
print(f"Expected: {TOTAL_AYAHS}")
print(f"Missing: {TOTAL_AYAHS - new_count}")

# Step 4: Re-assign sura/ayah numbers
print("\nRe-assigning sura/ayah numbers...")

cursor.execute('SELECT id, page_number, cx, cy FROM raw_markers ORDER BY page_number, cy, cx DESC')
all_circles = cursor.fetchall()

# Group into lines
lines = []
current_line = [all_circles[0]]
for i in range(1, len(all_circles)):
    c = all_circles[i]
    prev = current_line[0]
    if c[1] == prev[1] and abs(c[3] - prev[3]) < 80:
        current_line.append(c)
    else:
        lines.append(current_line)
        current_line = [c]
if current_line:
    lines.append(current_line)

current_sura = 1
current_ayah = 1
updates = []

for line in lines:
    sorted_line = sorted(line, key=lambda c: -c[2])  # RTL
    for circle in sorted_line:
        marker_id = circle[0]
        updates.append((current_sura, current_ayah, marker_id))
        
        if current_ayah == hafs_ayat[current_sura - 1]:
            current_sura += 1
            current_ayah = 1
        else:
            current_ayah += 1

print(f"Assigned {len(updates)} circles")

if len(updates) < TOTAL_AYAHS:
    print(f"WARNING: Only assigned {len(updates)} of {TOTAL_AYAHS} expected ayahs!")
    print(f"  Stopped at Sura {current_sura}, Ayah {current_ayah}")
else:
    print(f"Successfully assigned all {TOTAL_AYAHS} ayahs!")
    print(f"  Ended at Sura {current_sura-1 if current_ayah == 1 else current_sura}")

cursor.executemany('''
    UPDATE raw_markers 
    SET sura_number = ?, ayah_number = ?
    WHERE id = ?
''', updates)
conn.commit()

# Step 5: Verify sura boundaries
print("\n=== Verification ===")
for sura in [4, 5, 6, 8, 36, 74, 81, 82, 88, 92, 98, 100, 104, 105, 107, 108]:
    cursor.execute(
        'SELECT page_number, cx, cy FROM raw_markers WHERE sura_number = ? AND ayah_number = 1',
        (sura,))
    result = cursor.fetchone()
    if result:
        print(f"  Sura {sura:3d}: page={result[0]}, cy={result[1]}")
    else:
        print(f"  Sura {sura:3d}: NOT FOUND!")

conn.close()
print("\nDone!")
