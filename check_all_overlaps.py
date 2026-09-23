import sqlite3

hafs_ayat = [7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111,
             43, 52, 99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77,
             227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75,
             85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55,
             78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52,
             44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25,
             22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
             11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6]

conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo.db')
c = conn.cursor()

print("="*60)
print("COMPREHENSIVE CHECK FOR ALL 114 SURAS")
print("="*60)

for s in range(2, 115):
    # Where does previous sura end?
    prev_s = s - 1
    prev_end_ayah = hafs_ayat[prev_s - 1]
    
    c.execute('''
        SELECT page, line, "left", "right" 
        FROM ayah_highlights 
        WHERE sura = ? AND ayah = ? 
        ORDER BY page DESC, line DESC LIMIT 1
    ''', (prev_s, prev_end_ayah))
    prev_end = c.fetchone()
    
    # Where does this sura start?
    c.execute('''
        SELECT page, line, "left", "right" 
        FROM ayah_highlights 
        WHERE sura = ? AND ayah = 1 
        ORDER BY page ASC, line ASC
    ''', (s,))
    curr_start_rows = c.fetchall()
    
    if not curr_start_rows:
        print(f"ERROR: Sura {s} has NO ayah 1!")
        continue
        
    curr_start_p = curr_start_rows[0][0]
    curr_start_l = curr_start_rows[0][1]
    
    # Mid-page transition
    if prev_end[0] == curr_start_p:
        prev_l = prev_end[1]
        line_gap = curr_start_l - prev_l
        # If line_gap < 3 (or < 2 for Sura 9):
        expected_gap = 2 if s == 9 else 3
        if line_gap < expected_gap:
            print(f"[ERROR - MID-PAGE OVERLAP] Sura {s} (Page {curr_start_p}): Prev Sura {prev_s}:{prev_end_ayah} ends at line {prev_l}, Sura {s}:1 starts at line {curr_start_l} (gap={line_gap}, expected={expected_gap})")
        elif line_gap > expected_gap:
            # Check if intervening lines are legitimately part of Ayah 1 or if Ayah 1 starts too late
            print(f"[CHECK - LARGE GAP] Sura {s} (Page {curr_start_p}): Prev Sura {prev_s}:{prev_end_ayah} ends at line {prev_l}, Sura {s}:1 starts at line {curr_start_l} (gap={line_gap})")
    else:
        # Sura starts on new page
        # Expected: line 3 (or line 2 for Sura 9)
        expected_line = 2 if s == 9 else 3
        if curr_start_l < expected_line:
            print(f"[ERROR - NEW-PAGE EARLY] Sura {s} (Page {curr_start_p}): Starts on line {curr_start_l} (expected line {expected_line})")
        elif curr_start_l > expected_line:
            print(f"[CHECK - NEW-PAGE LATE] Sura {s} (Page {curr_start_p}): Starts on line {curr_start_l} (expected line {expected_line})")
            
    # Check if any segment of Ayah 1 is on a Header or Bismillah line
    # On new page: Line 1 = Header, Line 2 = Bismillah
    # On mid-page (where prev ends at prev_l): prev_l + 1 = Header, prev_l + 2 = Bismillah
    for r in curr_start_rows:
        pg, l, left, right = r
        if prev_end[0] == pg:
            header_l = prev_end[1] + 1
            bismillah_l = prev_end[1] + 2 if s != 9 else -1
        else:
            header_l = 1
            bismillah_l = 2 if s != 9 else -1
            
        if l == header_l:
            print(f"[ERROR - HIGHLIGHT ON HEADER] Sura {s}:1 has highlight on line {l} (Header) of Page {pg}!")
        if l == bismillah_l:
            print(f"[ERROR - HIGHLIGHT ON BISMILLAH] Sura {s}:1 has highlight on line {l} (Bismillah) of Page {pg}!")

print("\nDone auditing.")
