import sqlite3

hafs_ayat = [7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111,
             43, 52, 99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77,
             227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75,
             85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55,
             78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52,
             44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25,
             22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
             11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6]

conn = sqlite3.connect(r'D:\Dev\Temp\Backup\ayahinfo.db')
c = conn.cursor()

print("Checking every Sura in ayahinfo.db...")

issues = []

for sura in range(1, 115):
    # Check all lines where Sura starts
    c.execute('SELECT page, line, "left", "right" FROM ayah_highlights WHERE sura = ? AND ayah = 1 ORDER BY page, line', (sura,))
    a1_rows = c.fetchall()
    
    if not a1_rows:
        issues.append(f"Sura {sura}: Missing Ayah 1!")
        continue
        
    start_page = a1_rows[0][0]
    start_line = a1_rows[0][1]
    
    if sura > 1:
        prev_sura = sura - 1
        prev_total = hafs_ayat[prev_sura - 1]
        c.execute('SELECT page, line, "left", "right" FROM ayah_highlights WHERE sura = ? AND ayah = ? ORDER BY page DESC, line DESC', (prev_sura, prev_total))
        prev_rows = c.fetchall()
        
        if not prev_rows:
            issues.append(f"Sura {prev_sura}: Missing last Ayah ({prev_total})!")
            continue
            
        last_prev_page = prev_rows[0][0]
        last_prev_line = prev_rows[0][1]
        
        if last_prev_page == start_page:
            gap = start_line - last_prev_line
            # Expected gap:
            # Sura Header takes 1 line
            # Bismillah takes 1 line (except Sura 9 which has 0 lines)
            # So gap should normally be 3 (prev ends line L, header is L+1, bismillah is L+2, Ayah 1 is L+3)
            # If Sura 9: gap should be 2 (prev ends L, header L+1, Ayah 1 L+2)
            expected_gap = 2 if sura == 9 else 3
            if gap != expected_gap:
                issues.append(f"Sura {sura} (Page {start_page}): Prev Sura {prev_sura} ends at line {last_prev_line}, but Sura {sura}:1 starts at line {start_line}. Gap = {gap} (expected {expected_gap})")
        else:
            # Starts on new page
            # On a new page:
            # Line 1: Header
            # Line 2: Bismillah
            # Line 3: Ayah 1
            # (Except Sura 1 which has Fatiha on p1, and Sura 9 which has header on Line 1, Ayah 1 on Line 2)
            expected_start_line = 1 if sura == 1 else (2 if sura == 9 else 3)
            if start_line != expected_start_line:
                issues.append(f"Sura {sura} (New Page {start_page}): Ayah 1 starts on Line {start_line} (expected {expected_start_line})")

    # Also check: does Ayah 1 have multiple segments?
    # If it has a full-line segment right before its first circle, is that a Header/Bismillah line?
    if len(a1_rows) > 1:
        # Check all lines except the last line of Ayah 1
        for row in a1_rows[:-1]:
            pg, l, left, right = row
            # If this line is empty text or full line (0.0 to ~1.0)
            if abs(right - left) > 0.85:
                # Let's check what line it is relative to the page
                # If on a mid-page start, is it the Bismillah line?
                print(f"Notice: Sura {sura}:1 has full line segment on Page {pg} Line {l}: {left:.3f} to {right:.3f}")

print("\n--- ALL ISSUES FOUND ---")
for iss in issues:
    print(" ", iss)
