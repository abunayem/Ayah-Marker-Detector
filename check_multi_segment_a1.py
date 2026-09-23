import sqlite3

conn = sqlite3.connect(r'D:\Dev\Temp\Backup\ayahinfo.db')
c = conn.cursor()

# Find all suras where Ayah 1 has more than 1 segment on its starting page
for s in range(1, 115):
    c.execute('SELECT page, line, "left", "right" FROM ayah_highlights WHERE sura = ? AND ayah = 1 ORDER BY page, line', (s,))
    rows = c.fetchall()
    if len(rows) > 1:
        pages = set(r[0] for r in rows)
        print(f"Sura {s:3d}: Ayah 1 has {len(rows)} segments on page(s) {pages}:")
        for r in rows:
            print(f"    Page {r[0]} Line {r[1]:2d}: {r[2]:.3f} to {r[3]:.3f}")
