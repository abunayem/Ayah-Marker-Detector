import sqlite3

conn = sqlite3.connect(r'D:\Dev\Temp\Backup\ayahinfo.db')
c = conn.cursor()

c.execute('SELECT line, sura, ayah, "left", "right" FROM ayah_highlights WHERE page = 591 ORDER BY line, "right" DESC')
for l, s, a, left, right in c.fetchall():
    print(f"Line {l:2d} | Sura {s:3d}:{a:<3d} | {left:.3f} to {right:.3f}")
