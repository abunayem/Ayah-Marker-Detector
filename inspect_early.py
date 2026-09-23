import sqlite3

conn = sqlite3.connect(r'D:\Dev\Temp\Backup\ayahinfo.db')
c = conn.cursor()

def inspect(sura_num):
    print(f"=== SURA {sura_num} ===")
    c.execute('SELECT page, line, ayah, "left", "right" FROM ayah_highlights WHERE sura = ? AND ayah <= 2 ORDER BY ayah, page, line', (sura_num,))
    for r in c.fetchall():
        print(f"  Ayah {r[2]} | Page {r[0]} Line {r[1]:2d} | {r[3]:.3f} to {r[4]:.3f}")

for s in [4, 5, 6, 8, 13, 16, 17, 18, 21, 24, 33, 34, 35, 36, 74]:
    inspect(s)
