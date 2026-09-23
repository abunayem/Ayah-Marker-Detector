import sqlite3

conn = sqlite3.connect(r'D:\Dev\Temp\Backup\ayahinfo.db')
c = conn.cursor()

for s in [81, 82]:
    print(f"=== Sura {s} ===")
    c.execute('SELECT page, line, sura, ayah, "left", "right" FROM ayah_highlights WHERE sura = ? ORDER BY ayah, line', (s,))
    for row in c.fetchall():
        print(f"Ayah {row[3]:2d} | Page {row[0]} Line {row[1]:2d} | left: {row[4]:.3f}, right: {row[5]:.3f}")
