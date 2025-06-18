import docker
import sqlite3
from datetime import datetime
import os

# Connexion à la base (créée si elle n'existe pas)
conn = sqlite3.connect("container_logs.db")
cursor = conn.cursor()

# Création de la table si elle n'existe pas
cursor.execute("""
    CREATE TABLE IF NOT EXISTS container_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        image TEXT,
        status TEXT,
        timestamp TEXT
    )
""")
conn.commit()

# Récupération des conteneurs
client = docker.from_env()
containers = client.containers.list(all=True)

# Insertion des états actuels dans la base
for c in containers:
    cursor.execute("""
        INSERT INTO container_events (name, image, status, timestamp)
        VALUES (?, ?, ?, ?)
    """, (
        c.name,
        c.image.tags[0] if c.image.tags else "inconnu",
        c.status,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

conn.commit()
conn.close()
print("✔️ Logs insérés dans container_logs.db")
