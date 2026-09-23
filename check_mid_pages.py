import sqlite3

conn = sqlite3.connect(r'D:\Dev\Temp\Backup\ayahinfo.db')
c = conn.cursor()

def check_trans(sura, pg):
    print(f"=== Sura {sura} on Page {pg} ===")
    c.execute('SELECT line, sura, ayah, "left", "right" FROM ayah_highlights WHERE page = ? AND (sura = ? OR (sura = ? AND ayah = 1)) ORDER BY line, "right" DESC', (pg, sura - 1, sura))
    rows = c.fetchall()
    for l, s, a, left, right in rows[-8:]:
        print(f"  Line {l:2d} | Sura {s:3d}:{a:<3d} | {left:.3f} to {right:.3f}")

for s, p in [(14, 255), (16, 267), (35, 434), (49, 515), (62, 553), (63, 554), (68, 564), (71, 571), (82, 591)]:
    check_trans(s, p)
