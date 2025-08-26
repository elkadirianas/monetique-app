import random, time
from datetime import datetime
import psycopg2
from psycopg2 import OperationalError

DSN = "dbname=sourcedb user=source password=source host=postgres_source port=5432"

ifaces = ["ATM", "POS", "VISA", "MASTERCARD"]
statuses = ["ACCEPTED", "REJECT_TECH", "REJECT_FUNC"]

def insert_tx():
    conn = psycopg2.connect(DSN)
    cur = conn.cursor()
    tx = (
        random.choice(ifaces),
        datetime.now(),
        random.choice(statuses),
        round(random.uniform(10, 500), 2)
    )
    cur.execute(
        "INSERT INTO transactions (iface, ts, status, amount) VALUES (%s, %s, %s, %s)", tx
    )
    conn.commit()
    cur.close(); conn.close()

if __name__ == "__main__":
    while True:
        try:
            insert_tx()
            print("Inserted transaction at", datetime.now())
            time.sleep(2)
        except OperationalError as e:
            print("DB not ready, retrying...", e)
            time.sleep(5)
