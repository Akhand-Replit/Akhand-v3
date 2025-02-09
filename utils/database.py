import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            host=os.getenv('PGHOST'),
            port=os.getenv('PGPORT')
        )
        self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cur:
            # Create batches table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS batches (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create records table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id SERIAL PRIMARY KEY,
                    batch_id INTEGER REFERENCES batches(id),
                    file_name VARCHAR(255),
                    ক্রমিক_নং VARCHAR(50),
                    নাম TEXT,
                    ভোটার_নং VARCHAR(100),
                    পিতার_নাম TEXT,
                    মাতার_নাম TEXT,
                    পেশা TEXT,
                    জন্ম_তারিখ VARCHAR(100),
                    ঠিকানা TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()

    def clear_all_data(self):
        """Clear all data from the database"""
        with self.conn.cursor() as cur:
            cur.execute("TRUNCATE records CASCADE")
            cur.execute("TRUNCATE batches CASCADE")
            self.conn.commit()

    def get_batch_files(self, batch_id):
        """Get unique files in a batch"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT DISTINCT file_name
                FROM records
                WHERE batch_id = %s
                ORDER BY file_name
            """, (batch_id,))
            return cur.fetchall()

    def get_file_records(self, batch_id, file_name):
        """Get records for a specific file in a batch"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT r.*, b.name as batch_name
                FROM records r
                JOIN batches b ON r.batch_id = b.id
                WHERE r.batch_id = %s AND r.file_name = %s
                ORDER BY r.created_at DESC
            """, (batch_id, file_name))
            return cur.fetchall()

    def add_batch(self, batch_name):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO batches (name) VALUES (%s) RETURNING id, name, created_at",
                (batch_name,)
            )
            result = cur.fetchone()
            self.conn.commit()
            return result['id']

    def add_record(self, batch_id, file_name, record_data):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO records (
                    batch_id, file_name, ক্রমিক_নং, নাম, ভোটার_নং,
                    পিতার_নাম, মাতার_নাম, পেশা, জন্ম_তারিখ, ঠিকানা
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                batch_id, file_name,
                record_data.get('ক্রমিক_নং'), record_data.get('নাম'),
                record_data.get('ভোটার_নং'), record_data.get('পিতার_নাম'),
                record_data.get('মাতার_নাম'), record_data.get('পেশা'),
                record_data.get('জন্ম_তারিখ'), record_data.get('ঠিকানা')
            ))
            self.conn.commit()

    def search_records_advanced(self, criteria):
        """
        Advanced search with multiple criteria
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT r.*, b.name as batch_name, r.file_name
                FROM records r
                JOIN batches b ON r.batch_id = b.id
                WHERE 1=1
            """
            params = []

            for field, value in criteria.items():
                if value:
                    query += f" AND {field} ILIKE %s"
                    params.append(f"%{value}%")

            query += " ORDER BY r.created_at DESC"

            logger.info(f"Executing search query: {query}")
            cur.execute(query, params)
            return cur.fetchall()

    def search_records(self, search_term):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT r.*, b.name as batch_name, r.file_name
                FROM records r
                JOIN batches b ON r.batch_id = b.id
                WHERE 
                    নাম ILIKE %s OR
                    পিতার_নাম ILIKE %s OR
                    মাতার_নাম ILIKE %s OR
                    ঠিকানা ILIKE %s
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            return cur.fetchall()

    def get_all_batches(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM batches ORDER BY created_at DESC")
            return cur.fetchall()

    def get_batch_records(self, batch_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            if batch_id is None:
                cur.execute("""
                    SELECT r.*, b.name as batch_name, r.file_name
                    FROM records r
                    JOIN batches b ON r.batch_id = b.id
                    ORDER BY r.created_at DESC
                """)
            else:
                cur.execute("""
                    SELECT r.*, b.name as batch_name, r.file_name
                    FROM records r
                    JOIN batches b ON r.batch_id = b.id
                    WHERE r.batch_id = %s
                    ORDER BY r.created_at DESC
                """, (batch_id,))
            return cur.fetchall()

    def get_occupation_stats(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT পেশা, COUNT(*) as count
                FROM records
                GROUP BY পেশা
                ORDER BY count DESC
            """)
            return cur.fetchall()