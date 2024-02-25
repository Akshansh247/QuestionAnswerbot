import sqlite3

conn = sqlite3.connect("./db.sqlite3")
cur = conn.cursor()

for k in range(1, 5, 1):
    rats = [float(x) for x in open(f"r{k}.csv").read().split("\n") if x]
    u_id = 8 + k
    q_id = 57
    for rat in rats:
        cur.execute(
            "Insert into api_rating (value, quiz_id, user_id) values (?, ?, ?)",
            (rat, q_id, u_id),
        )
        q_id += 1
conn.commit()
