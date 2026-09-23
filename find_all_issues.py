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

problem_suras = []

for sura in range(1, 115):
    c.execute('SELECT page, line, "left", "right" FROM ayah_highlights WHERE sura = ? AND ayah = 1 ORDER BY page, line', (sura,))
    rows = c.fetchall()
    if not rows:
        print(f"Sura {sura:3d}: AYAH 1 MISSING COMPLETELY!")
        problem_suras.append(sura)
        continue
    
    first_row = rows[0]
    first_page = first_row[0]
    first_line = first_row[1]
    
    prev_sura = sura - 1
    if prev_sura >= 1:
        # Get the actual last segment of the previous sura
        c.execute('SELECT page, line FROM ayah_highlights WHERE sura = ? AND ayah = ? ORDER BY page DESC, line DESC LIMIT 1', 
                  (prev_sura, hafs_ayat[prev_sura-1]))
        last_seg = c.fetchone()
        
        if last_seg and last_seg[0] == first_page:
            prev_line = last_seg[1]
            diff = first_line - prev_line
            # Standard transition has Sura Header (1 line) + Bismillah (1 line) -> diff should be 3
            # Sura 9 has no Bismillah -> diff should be 2
            expected_diff = 2 if sura == 9 else 3
            if diff != expected_diff:
                print(f"[MID-PAGE ISSUE] Sura {sura:3d} (Page {first_page}): Prev Sura ended line {prev_line}, Sura {sura}:1 starts line {first_line} (diff={diff}, expected={expected_diff})")
                problem_suras.append(sura)
        else:
            # Sura starts on new page
            # Standard new page start has Header (Line 1) + Bismillah (Line 2) -> Ayah 1 starts on Line 3
            # Sura 9 has no Bismillah -> Line 2
            expected_line = 2 if sura == 9 else 3
            if first_line != expected_line:
                print(f"[NEW-PAGE ISSUE] Sura {sura:3d} (Page {first_page}): Sura {sura}:1 starts on Line {first_line} (expected={expected_line})")
                problem_suras.append(sura)

print(f"\nTotal problem Suras: {len(problem_suras)}")
print("Problem Suras:", problem_suras)
