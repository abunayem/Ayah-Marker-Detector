import sqlite3

db_path = r'D:\Dev\Temp\db\nasiha_v2.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='ayah_highlights'")
schema = cursor.fetchone()
if schema:
    print('Schema:')
    print(schema[0])
else:
    print('Table ayah_highlights not found.')

cursor.execute("SELECT * FROM ayah_highlights LIMIT 5")
rows = cursor.fetchall()
print('\nSample data:')
for r in rows:
    print(r)

cursor.execute("SELECT COUNT(*) FROM ayah_highlights")
count = cursor.fetchone()[0]
print('\nTotal rows:', count)

conn.close()
