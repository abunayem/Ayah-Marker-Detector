import sqlite3

conn = sqlite3.connect(r'D:\Dev\Temp\Backup\ayahinfo.db')
c = conn.cursor()

def dump_range(pg, l1, l2):
    print(f"=== Page {pg} (lines {l1}-{l2}) ===")
    c.execute('SELECT line, sura, ayah, "left", "right" FROM ayah_highlights WHERE page = ? AND line BETWEEN ? AND ? ORDER BY line, "right" DESC', (pg, l1, l2))
    for r in c.fetchall():
        print(f"  Line {r[0]:2d} | Sura {r[1]:3d}:{r[2]:<3d} | {r[3]:.3f} to {r[4]:.3f}")

dump_range(106, 4, 11)
