"""
Comprehensive fix for Bismillah circle contamination in raw_markers.

The problem: The circle detector sometimes picks up the small decorative circle
at the end of the Bismillah line (بسم الله الرحمن الرحيم ○). This circle is NOT
an ayah marker, but recalculate_ayahs.py counts it as one, shifting all
subsequent sura/ayah numbering forward by 1 for every false Bismillah circle.

The fix:
1. Process all circles in page/cy reading order
2. Group them into text lines (circles within 80px of cy on the same page)
3. Do a trial sequential assignment
4. At each sura transition, check if the next circle is a Bismillah circle
5. A Bismillah circle is identified as: the first circle after a sura ends,
   which is isolated (only circle on its text line) and has empty lines
   between it and the previous circle group (the sura header gap).
6. Remove identified Bismillah circles from the database
7. Re-run sequential assignment with corrected data
"""

import sqlite3
import os

DB_PATH = r'D:\Dev\Temp\ayahinfo_emdadia_perfect.db'

hafs_ayat = [7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111,
             43, 52, 99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77,
             227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75,
             85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55,
             78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52,
             44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25,
             22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
             11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6]

TOTAL_AYAHS = sum(hafs_ayat)  # 6236

def group_into_lines(circles):
    """Group circles into text lines based on cy proximity.
    circles is a list of (id, page, cx, cy) sorted by (page, cy).
    Returns list of lists, each sublist is circles on the same line.
    """
    if not circles:
        return []
    
    lines = []
    current_line = [circles[0]]
    
    for i in range(1, len(circles)):
        c = circles[i]
        prev = current_line[0]
        
        # Same page and within 80px vertically = same line
        if c[1] == prev[1] and abs(c[3] - prev[3]) < 80:
            current_line.append(c)
        else:
            lines.append(current_line)
            current_line = [c]
    
    if current_line:
        lines.append(current_line)
    
    return lines


def find_bismillah_circles(lines):
    """Identify Bismillah circles by doing a trial sequential assignment.
    
    At each sura transition, check if the first circle after the transition
    is a Bismillah circle (isolated on its line with a gap before it).
    """
    bismillah_ids = set()
    
    # Flatten all circles in reading order (within each line, sort RTL by -cx)
    ordered_circles = []
    for line in lines:
        # Sort RTL within line
        sorted_line = sorted(line, key=lambda c: -c[2])
        ordered_circles.extend(sorted_line)
    
    # Trial sequential assignment
    current_sura = 1
    current_ayah = 0  # Will become 1 on first circle
    
    idx = 0
    while idx < len(ordered_circles):
        circle = ordered_circles[idx]
        current_ayah += 1
        
        # Check if this ayah completes the current sura
        if current_ayah == hafs_ayat[current_sura - 1]:
            # Sura just ended. The NEXT circle should be the first ayah of the next sura.
            # But there might be a Bismillah circle in between.
            
            next_sura = current_sura + 1
            if next_sura > 114:
                break  # We're done
            
            # Look ahead: is the next circle a Bismillah circle?
            if idx + 1 < len(ordered_circles):
                next_circle = ordered_circles[idx + 1]
                
                # For all suras except Sura 9 (At-Tawbah), there's a Bismillah
                if next_sura != 9:
                    # Check if next_circle is a Bismillah circle:
                    # 1. Find which line it belongs to
                    next_line = None
                    next_line_idx = None
                    for li, line in enumerate(lines):
                        for c in line:
                            if c[0] == next_circle[0]:
                                next_line = line
                                next_line_idx = li
                                break
                        if next_line:
                            break
                    
                    if next_line and len(next_line) == 1:
                        # This circle is alone on its line. Check for gap.
                        # Current circle's line:
                        curr_line_idx = None
                        for li, line in enumerate(lines):
                            for c in line:
                                if c[0] == circle[0]:
                                    curr_line_idx = li
                                    break
                            if curr_line_idx is not None:
                                break
                        
                        if curr_line_idx is not None and next_line_idx is not None:
                            gap = next_line_idx - curr_line_idx
                            # If there's a gap of 2+ lines (header + Bismillah),
                            # and this is the only circle in between, it's a Bismillah circle
                            if gap >= 2:
                                # Verify no other circles exist in the gap
                                circles_in_gap = []
                                for li in range(curr_line_idx + 1, next_line_idx):
                                    circles_in_gap.extend(lines[li])
                                
                                if len(circles_in_gap) == 0:
                                    # This IS a Bismillah circle!
                                    bismillah_ids.add(next_circle[0])
                                    print(f"  Found Bismillah circle: id={next_circle[0]}, "
                                          f"page={next_circle[1]}, cx={next_circle[2]}, cy={next_circle[3]}, "
                                          f"between Sura {current_sura} and {next_sura}, gap={gap} lines")
                                    idx += 1  # Skip the Bismillah circle
                    
                    elif next_line and len(next_line) > 1:
                        # Multiple circles on this line - not a Bismillah circle
                        pass
            
            current_sura = next_sura
            current_ayah = 0
        
        idx += 1
    
    return bismillah_ids


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all circles sorted by page and cy
    cursor.execute('SELECT id, page_number, cx, cy FROM raw_markers ORDER BY page_number, cy, cx DESC')
    all_circles = cursor.fetchall()
    
    print(f"Total circles in database: {len(all_circles)}")
    print(f"Expected total ayahs: {TOTAL_AYAHS}")
    print()
    
    # Group into lines
    lines = group_into_lines(all_circles)
    print(f"Total text lines: {len(lines)}")
    print()
    
    # Find Bismillah circles
    print("Scanning for Bismillah circles...")
    bismillah_ids = find_bismillah_circles(lines)
    
    print(f"\nFound {len(bismillah_ids)} Bismillah circles")
    
    if bismillah_ids:
        print("\nDeleting Bismillah circles from database...")
        for bid in bismillah_ids:
            cursor.execute('DELETE FROM raw_markers WHERE id = ?', (bid,))
        conn.commit()
        print(f"Deleted {len(bismillah_ids)} Bismillah circles")
    
    # Verify new count
    cursor.execute('SELECT COUNT(*) FROM raw_markers')
    new_count = cursor.fetchone()[0]
    print(f"\nNew total circles: {new_count}")
    print(f"Expected: {TOTAL_AYAHS}")
    print(f"Difference: {new_count - TOTAL_AYAHS}")
    
    # Now re-assign sura/ayah numbers
    print("\nRe-assigning sura/ayah numbers...")
    cursor.execute('SELECT id, page_number, cx, cy FROM raw_markers ORDER BY page_number, cy, cx DESC')
    all_circles = cursor.fetchall()
    
    lines = group_into_lines(all_circles)
    
    current_sura = 1
    current_ayah = 1
    updates = []
    
    for line in lines:
        # Sort RTL within line
        sorted_line = sorted(line, key=lambda c: -c[2])
        
        for circle in sorted_line:
            marker_id = circle[0]
            updates.append((current_sura, current_ayah, marker_id))
            
            if current_ayah == hafs_ayat[current_sura - 1]:
                current_sura += 1
                current_ayah = 1
            else:
                current_ayah += 1
    
    print(f"Assigned {len(updates)} circles")
    print(f"Ended at Sura {current_sura - 1 if current_ayah == 1 else current_sura}, "
          f"Ayah {hafs_ayat[current_sura - 2] if current_ayah == 1 else current_ayah - 1}")
    
    cursor.executemany('''
        UPDATE raw_markers 
        SET sura_number = ?, ayah_number = ?
        WHERE id = ?
    ''', updates)
    
    conn.commit()
    
    # Verify a few known sura boundaries
    print("\n--- Verification ---")
    for sura in [4, 5, 6, 8, 13, 16, 17, 18, 21, 24, 33, 34, 35, 36, 
                 74, 81, 82, 88, 92, 95, 98, 100, 104, 105, 107, 108]:
        cursor.execute(
            'SELECT page_number, cx, cy FROM raw_markers WHERE sura_number = ? AND ayah_number = 1',
            (sura,))
        result = cursor.fetchone()
        if result:
            print(f"  Sura {sura:3d} Ayah 1: page={result[0]}, cx={result[1]}, cy={result[2]}")
        else:
            print(f"  Sura {sura:3d} Ayah 1: NOT FOUND!")
    
    conn.close()
    print("\nDone!")


if __name__ == '__main__':
    main()
