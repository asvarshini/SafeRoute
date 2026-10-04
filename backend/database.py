import sqlite3
import json

DB_NAME = "saferoute.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price INTEGER,
            rating REAL,
            hygiene_score REAL,
            womens_safety_score REAL,
            hygiene_evidence TEXT,
            safety_evidence TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS community_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            category TEXT NOT NULL,
            experience TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hotel_id) REFERENCES hotels(id)
        )
    """)

    conn.commit()
    conn.close()


def save_hotel(hotel):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO hotels (
            name,
            price,
            rating,
            hygiene_score,
            womens_safety_score,
            hygiene_evidence,
            safety_evidence
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(name) DO UPDATE SET
            price = excluded.price,
            rating = excluded.rating,
            hygiene_score = excluded.hygiene_score,
            womens_safety_score = excluded.womens_safety_score,
            hygiene_evidence = excluded.hygiene_evidence,
            safety_evidence = excluded.safety_evidence
    """, (
        hotel["name"],
        hotel["price"],
        hotel["rating"],
        hotel["hygiene_score"],
        hotel["womens_safety_score"],
        json.dumps(hotel["hygiene_evidence"]),
        json.dumps(hotel["safety_evidence"])
    ))

    cursor.execute(
        "SELECT id FROM hotels WHERE name = ?",
        (hotel["name"],)
    )

    row = cursor.fetchone()

    conn.commit()
    conn.close()

    if row:
        return row[0]

    return None


def get_hotel_id(name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM hotels WHERE name = ?",
        (name,)
    )

    row = cursor.fetchone()

    conn.close()

    return row[0] if row else None


create_tables()