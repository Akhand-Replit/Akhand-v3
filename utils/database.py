import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # Set client encoding to UTF8 explicitly
        self.conn = psycopg2.connect(
            dbname=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            host=os.getenv('PGHOST'),
            port=os.getenv('PGPORT'),
            options="-c client_encoding=utf8"
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

            # Create records table with explicit encoding
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

            # Drop and recreate relationships table with proper structure
            cur.execute("DROP TABLE IF EXISTS relationships CASCADE")
            cur.execute("""
                CREATE TABLE relationships (
                    id SERIAL PRIMARY KEY,
                    record_id INTEGER REFERENCES records(id) ON DELETE CASCADE,
                    ক্রমিক_নং VARCHAR(50),
                    নাম TEXT,
                    ভোটার_নং VARCHAR(100),
                    পিতার_নাম TEXT,
                    মাতার_নাম TEXT,
                    পেশা TEXT,
                    ঠিকানা TEXT,
                    batch_name VARCHAR(255),
                    file_name VARCHAR(255),
                    relationship_type VARCHAR(10) CHECK (relationship_type IN ('friend', 'enemy')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(record_id)
                )
            """)
            self.conn.commit()

    def clear_all_data(self):
        """Clear all data from the database"""
        with self.conn.cursor() as cur:
            cur.execute("TRUNCATE records CASCADE")
            cur.execute("TRUNCATE batches CASCADE")
            cur.execute("TRUNCATE relationships CASCADE") #added this line
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

    def update_record(self, record_id, updated_data):
        """Update a record with new data"""
        with self.conn.cursor() as cur:
            query = """
                UPDATE records SET
                    ক্রমিক_নং = %s,
                    নাম = %s,
                    ভোটার_নং = %s,
                    পিতার_নাম = %s,
                    মাতার_নাম = %s,
                    পেশা = %s,
                    ঠিকানা = %s,
                    জন্ম_তারিখ = %s
                WHERE id = %s
            """
            # Ensure all values are strings or None
            values = (
                str(updated_data.get('ক্রমিক_নং', '')),
                str(updated_data.get('নাম', '')),
                str(updated_data.get('ভোটার_নং', '')),
                str(updated_data.get('পিতার_নাম', '')),
                str(updated_data.get('মাতার_নাম', '')),
                str(updated_data.get('পেশা', '')),
                str(updated_data.get('ঠিকানা', '')),
                str(updated_data.get('জন্ম_তারিখ', '')),
                record_id
            )
            cur.execute(query, values)
            self.conn.commit()


    def search_records_advanced(self, criteria):
        """
        Advanced search with multiple criteria
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT r.*, b.name as batch_name
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
                SELECT r.*, b.name as batch_name
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
                    SELECT r.*, b.name as batch_name
                    FROM records r
                    JOIN batches b ON r.batch_id = b.id
                    ORDER BY r.created_at DESC
                """)
            else:
                cur.execute("""
                    SELECT r.*, b.name as batch_name
                    FROM records r
                    JOIN batches b ON r.batch_id = b.id
                    WHERE r.batch_id = %s
                    ORDER BY r.created_at DESC
                """, (batch_id,))
            return cur.fetchall()

    def get_batch_occupation_stats(self, batch_id):
        """Get occupation statistics for a specific batch"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT পেশা, COUNT(*) as count
                FROM records
                WHERE batch_id = %s
                GROUP BY পেশা
                ORDER BY count DESC
            """, (batch_id,))
            return cur.fetchall()

    def get_occupation_stats(self):
        """Get overall occupation statistics"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT পেশা, COUNT(*) as count
                FROM records
                GROUP BY পেশা
                ORDER BY count DESC
            """)
            return cur.fetchall()

    def add_relationship(self, record_id: int, relationship_type: str):
        """Add or update a relationship (friend/enemy) for a record"""
        try:
            record_id = int(record_id)  # Convert to native Python int

            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # First get the record details
                cur.execute("""
                    SELECT r.*, b.name as batch_name 
                    FROM records r
                    JOIN batches b ON r.batch_id = b.id
                    WHERE r.id = %s
                """, (record_id,))

                record = cur.fetchone()
                if not record:
                    raise ValueError(f"Record with ID {record_id} not found")

                # Ensure all text data is properly encoded
                record_data = {
                    'ক্রমিক_নং': str(record['ক্রমিক_নং']).encode('utf-8').decode('utf-8'),
                    'নাম': str(record['নাম']).encode('utf-8').decode('utf-8'),
                    'ভোটার_নং': str(record['ভোটার_নং']).encode('utf-8').decode('utf-8'),
                    'পিতার_নাম': str(record['পিতার_নাম']).encode('utf-8').decode('utf-8'),
                    'মাতার_নাম': str(record['মাতার_নাম']).encode('utf-8').decode('utf-8'),
                    'পেশা': str(record['পেশা']).encode('utf-8').decode('utf-8'),
                    'ঠিকানা': str(record['ঠিকানা']).encode('utf-8').decode('utf-8'),
                }

                # Insert or update relationship with copied data
                cur.execute("""
                    INSERT INTO relationships (
                        record_id, ক্রমিক_নং, নাম, ভোটার_নং, পিতার_নাম,
                        মাতার_নাম, পেশা, ঠিকানা, batch_name, file_name,
                        relationship_type
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (record_id) 
                    DO UPDATE SET
                        ক্রমিক_নং = EXCLUDED.ক্রমিক_নং,
                        নাম = EXCLUDED.নাম,
                        ভোটার_নং = EXCLUDED.ভোটার_নং,
                        পিতার_নাম = EXCLUDED.পিতার_নাম,
                        মাতার_নাম = EXCLUDED.মাতার_নাম,
                        পেশা = EXCLUDED.পেশা,
                        ঠিকানা = EXCLUDED.ঠিকানা,
                        batch_name = EXCLUDED.batch_name,
                        file_name = EXCLUDED.file_name,
                        relationship_type = EXCLUDED.relationship_type,
                        created_at = CURRENT_TIMESTAMP
                """, (
                    record_id,
                    record_data['ক্রমিক_নং'],
                    record_data['নাম'],
                    record_data['ভোটার_নং'],
                    record_data['পিতার_নাম'],
                    record_data['মাতার_নাম'],
                    record_data['পেশা'],
                    record_data['ঠিকানা'],
                    record['batch_name'],
                    record['file_name'],
                    relationship_type
                ))
                self.conn.commit()
                logger.info(f"Successfully added/updated relationship for record {record_id}")
        except Exception as e:
            logger.error(f"Error adding relationship: {str(e)}")
            self.conn.rollback()
            raise

    def remove_relationship(self, record_id: int):
        """Remove a relationship for a record"""
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM relationships WHERE record_id = %s", (record_id,))
            self.conn.commit()

    def get_relationships(self, relationship_type: str):
        """Get all records with a specific relationship type"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM relationships
                WHERE relationship_type = %s
                ORDER BY created_at DESC
            """, (relationship_type,))
            return cur.fetchall()