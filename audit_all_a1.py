import sqlite3

conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo.db')
c = conn.cursor()

print("Listing all Ayah 1 line assignments across all 114 Suras:")
for s in range(1, 115):
    c.execute('SELECT page, line, "left", "right" FROM ayah_highlights WHERE sura = ? AND ayah = 1 ORDER BY page, line', (s,))
    rows = c.fetchall()
    if len(rows) > 1:
        print(f"Sura {s:3d} (Page {rows[0][0]}): {len(rows)} segments on lines {[r[1] for r in rows]}")
    elif len(rows) == 1:
        # Check if line is line 1 or line 2 on a new page (which would be Header or Bismillah!)
        pg, l, left, right = rows[0]
        # Does this Sura start on a new page?
        if s > 1:
            prev_s = s - 1
            c.execute('SELECT MAX(page) FROM ayah_highlights WHERE sura = ?', (prev_s,))
            prev_pg = c.fetchone()[0]
            if prev_pg != pg:
                # New page start:
                if l < 3 and s != 9:
                    print(f"SUSPICIOUS NEW-PAGE: Sura {s:3d} (Page {pg}): Ayah 1 is on Line {l}!")
