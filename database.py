import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "db.dttiqptqokirducezdyp.supabase.co")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

def get_db_connection():
    """Create and return a connection to Supabase PostgreSQL database."""
    if not DB_PASSWORD or DB_PASSWORD == "YOUR_SUPABASE_PASSWORD_HERE":
        raise ValueError(
            "Database password is not set! Please set DB_PASSWORD in your .env file."
        )
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require",
        cursor_factory=RealDictCursor,
        connect_timeout=10
    )

def init_db(seed_data=None):
    """Initialize database tables and seed catalog if empty."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Products table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id VARCHAR(64) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(64) NOT NULL,
                    tag VARCHAR(64),
                    image TEXT,
                    description TEXT,
                    benefits JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 2. Product variants table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS product_variants (
                    id SERIAL PRIMARY KEY,
                    product_id VARCHAR(64) REFERENCES products(id) ON DELETE CASCADE,
                    size VARCHAR(64) NOT NULL,
                    price NUMERIC(10, 2) NOT NULL,
                    original_price NUMERIC(10, 2),
                    is_default BOOLEAN DEFAULT FALSE
                );
            """)

            # 3. Orders table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    order_ref VARCHAR(32) UNIQUE NOT NULL,
                    customer_name VARCHAR(255) NOT NULL,
                    customer_phone VARCHAR(32) NOT NULL,
                    customer_email VARCHAR(255),
                    delivery_address TEXT NOT NULL,
                    city VARCHAR(100) NOT NULL,
                    pincode VARCHAR(20) NOT NULL,
                    payment_method VARCHAR(50) DEFAULT 'UPI / Online',
                    total_amount NUMERIC(10, 2) NOT NULL,
                    status VARCHAR(50) DEFAULT 'Confirmed',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 4. Order items table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                    product_id VARCHAR(64),
                    product_name VARCHAR(255),
                    size VARCHAR(64),
                    unit_price NUMERIC(10, 2),
                    quantity INTEGER NOT NULL,
                    total_price NUMERIC(10, 2)
                );
            """)

            # Check if products already seeded
            cur.execute("SELECT COUNT(*) AS cnt FROM products;")
            row = cur.fetchone()
            count = row["cnt"] if row else 0

            if count == 0 and seed_data:
                for prod in seed_data:
                    cur.execute("""
                        INSERT INTO products (id, name, category, tag, image, description, benefits)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING;
                    """, (
                        prod["id"],
                        prod["name"],
                        prod["category"],
                        prod["tag"],
                        prod["image"],
                        prod["description"],
                        json.dumps(prod["benefits"])
                    ))

                    for variant in prod.get("variants", []):
                        cur.execute("""
                            INSERT INTO product_variants (product_id, size, price, original_price, is_default)
                            VALUES (%s, %s, %s, %s, %s);
                        """, (
                            prod["id"],
                            variant["size"],
                            variant["price"],
                            variant.get("originalPrice"),
                            variant.get("isDefault", False)
                        ))

        conn.commit()
        return {"status": "success", "message": "Database tables initialized and seeded successfully."}
    finally:
        conn.close()
