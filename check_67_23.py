import sqlite3

conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo.db')
c = conn.cursor()

c.execute('SELECT page, line, "left", "right" FROM ayah_highlights WHERE sura = 67 AND ayah IN (22, 23) ORDER BY ayah, page, line')
for r in c.fetchall():
    print(r)
