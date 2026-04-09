import psycopg2, os, random, time

print("Waiting for DB to be fully ready...")
time.sleep(5) 

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("POSTGRES_DB"), user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS taxi_trips (id SERIAL PRIMARY KEY, lat FLOAT, lon FLOAT);")

for _ in range(1000):
    lat = random.uniform(55.65, 55.85)
    lon = random.uniform(37.45, 37.75)
    cur.execute("INSERT INTO taxi_trips (lat, lon) VALUES (%s, %s)", (lat, lon))

conn.commit()
print("Taxi trip data loaded successfully!")
cur.close()
conn.close()