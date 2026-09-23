import sqlite3

conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo.db')
c = conn.cursor()

c.execute('SELECT line, sura, ayah, "left", "right" FROM ayah_highlights WHERE page = 565 AND line <= 2 ORDER BY line, "right" DESC')
for r in c.fetchall():
    print(r)
