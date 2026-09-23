import sqlite3

conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo.db')
c = conn.cursor()

print("=== Page 564 Highlights ===")
c.execute('SELECT line, sura, ayah, "left", "right" FROM ayah_highlights WHERE page = 564 ORDER BY line, "right" DESC')
for r in c.fetchall():
    print(f"Line {r[0]:2d} | Sura {r[1]:3d}:{r[2]:<3d} | {r[3]:.3f} to {r[4]:.3f}")

print("\n=== Page 564 Lines ===")
c.execute('SELECT line, top_pct, bottom_pct FROM page_lines WHERE page = 564 ORDER BY line')
for r in c.fetchall():
    print(f"Line {r[0]:2d} | {r[1]:.3f} to {r[2]:.3f}")
