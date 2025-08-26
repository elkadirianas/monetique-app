import psycopg2, time
from psycopg2 import OperationalError
from datetime import datetime

SRC_DSN = "dbname=sourcedb user=source password=source host=postgres_source port=5432"
APP_DSN = "dbname=appdb user=app password=app host=postgres_app port=5432"

def wait_for_db(dsn, name):
    while True:
        try:
            conn = psycopg2.connect(dsn)
            conn.close()
            print(f"{name} est prêt")
            return
        except OperationalError:
            print(f"waiting for {name}...")
            time.sleep(5)

def etl():
    wait_for_db(SRC_DSN, "Source DB")
    wait_for_db(APP_DSN, "App DB")

    src = psycopg2.connect(SRC_DSN)
    dst = psycopg2.connect(APP_DSN)
    src_cur, dst_cur = src.cursor(), dst.cursor()

    # Lire toutes les transactions sources
    src_cur.execute("SELECT id, iface, ts, status, amount FROM transactions")
    rows = src_cur.fetchall()

    inserted = 0
    # Optimization: collect all existing IDs first to avoid row-by-row SELECT
    dst_cur.execute("SELECT id FROM fact_transactions")
    existing_ids = set(row[0] for row in dst_cur.fetchall())

    for r in rows:
        if r[0] not in existing_ids:
            dst_cur.execute("""
                INSERT INTO fact_transactions(id, iface, ts, status, amount, etl_loaded_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (*r, datetime.now()))
            inserted += 1

    dst.commit()
    print(f"{inserted} inserted lines in table fact_transactions")  # Fixed typo

    src_cur.close(); dst_cur.close()
    src.close(); dst.close()

if __name__ == "__main__":
    while True:
        etl()
        time.sleep(10)