"""
Detailed diagnostic: examine the spatial layout around every sura transition
to understand why the recalculate_ayahs assignment is wrong.
"""
import sqlite3

DB_PATH = r'D:\Dev\Temp\ayahinfo_emdadia_perfect.db'

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

c.execute('SELECT id, page_number, cx, cy FROM raw_markers ORDER BY page_number, cy, cx DESC')
all_circles = c.fetchall()

# Group into lines
lines = []
current_line = [all_circles[0]]
for i in range(1, len(all_circles)):
    circ = all_circles[i]
    prev = current_line[0]
    if circ[1] == prev[1] and abs(circ[3] - prev[3]) < 80:
        current_line.append(circ)
    else:
        lines.append(current_line)
        current_line = [circ]
if current_line:
    lines.append(current_line)

# Now do sequential assignment and print details at each sura transition
print("=== Sura Transition Analysis ===")
print()

flat = []
for line_idx, line in enumerate(lines):
    sorted_line = sorted(line, key=lambda c: -c[2])
    for c in sorted_line:
        flat.append((c, line_idx, len(line)))

sura = 1
ayah = 1

for idx, (circle, line_idx, line_size) in enumerate(flat):
    cid, page, cx, cy = circle
    
    if ayah == hafs_ayat[sura - 1]:
        # This is the LAST ayah of this sura
        next_sura = sura + 1
        if next_sura > 114:
            break
        
        # Show context: this circle and the next few
        print(f"--- Sura {sura} ends (ayah {ayah}) ---")
        print(f"  Last circle: id={cid}, page={page}, cx={cx}, cy={cy}, "
              f"line={line_idx}, circles_on_line={line_size}")
        
        # Show next 5 circles
        for j in range(1, min(6, len(flat) - idx)):
            nc, nl, ns = flat[idx + j]
            ncid, npage, ncx, ncy = nc
            print(f"  +{j}: id={ncid}, page={npage}, cx={ncx}, cy={ncy}, "
                  f"line={nl}, circles_on_line={ns}")
        
        # Check: how many lines gap to the next circle?
        if idx + 1 < len(flat):
            next_c, next_line, next_size = flat[idx + 1]
            gap = next_line - line_idx
            print(f"  Gap to next circle: {gap} lines")
            if gap <= 1:
                print(f"  *** WARNING: NO GAP! Next circle is on same/adjacent line.")
                print(f"  *** This means the header+Bismillah is NOT creating a gap.")
                print(f"  *** The Bismillah circle might be getting grouped with adjacent text!")
        print()
        
        sura = next_sura
        ayah = 0  # Will be incremented below
    
    ayah += 1

conn.close()
