import sqlite3
conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo_emdadia_perfect.db')
c = conn.cursor()
c.execute("SELECT sql FROM sqlite_master WHERE name = 'raw_markers'")
print(c.fetchone()[0])
c.execute("SELECT MIN(id), MAX(id), COUNT(*) FROM raw_markers")
print(c.fetchone())
