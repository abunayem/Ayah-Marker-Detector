import sqlite3

conn = sqlite3.connect(r'D:\Dev\Temp\Backup\ayahinfo.db')
c = conn.cursor()

def dump_page(pg):
    print(f"=== Page {pg} ===")
    c.execute('SELECT line, top_pct, bottom_pct FROM page_lines WHERE page = ? ORDER BY line', (pg,))
    plines = c.fetchall()
    print(f"Total lines in page_lines: {len(plines)}")
    for l, t, b in plines:
        print(f"  Line {l:2d}: top={t:.3f}, bottom={b:.3f}")
        
    c.execute('SELECT line, sura, ayah, "left", "right" FROM ayah_highlights WHERE page = ? ORDER BY line, "right" DESC', (pg,))
    for l, s, a, left, right in c.fetchall():
        print(f"  Line {l:2d} | Sura {s:3d}:{a:<3d} | left: {left:.3f}, right: {right:.3f}")

dump_page(590)
dump_page(591)
dump_page(601)
