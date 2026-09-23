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

print(f"Total suras: {len(hafs_ayat)}")

for sura in range(1, 115):
    # Check start ayah
    c.execute('SELECT page, line, "left", "right" FROM ayah_highlights WHERE sura = ? AND ayah = 1 ORDER BY page, line', (sura,))
    rows = c.fetchall()
    if not rows:
        print(f"Sura {sura:3d}: AYAH 1 MISSING COMPLETELY!")
        continue
    
    # Check if ayah 1 starts on a page where previous sura also exists
    prev_sura = sura - 1
    if prev_sura >= 1:
        c.execute('SELECT MAX(page), MAX(line) FROM ayah_highlights WHERE sura = ? AND ayah = ?', (prev_sura, hafs_ayat[prev_sura-1]))
        prev_end = c.fetchone()
        first_row = rows[0]
        # If on the same page, check the line difference
        if prev_end and prev_end[0] == first_row[0]:
            line_diff = first_row[1] - prev_end[1]
            # Sura header + bismillah usually takes 2 lines, so first ayah should start at line_diff >= 2 or 3
            # If line_diff <= 0, ayah 1 is on or before the last ayah of previous sura!
            # If line_diff == 1, ayah 1 is on the Sura Header!
            # If line_diff == 2, ayah 1 might be on Bismillah!
            print(f"Sura {sura:3d} (mid-page {first_row[0]}): Prev Sura {prev_sura} ended at line {prev_end[1]}, Sura {sura}:1 starts at line {first_row[1]} (diff={line_diff}) | {len(rows)} segments")
        else:
            # New page
            print(f"Sura {sura:3d} (new-page {first_row[0]}): starts at line {first_row[1]} | {len(rows)} segments")
