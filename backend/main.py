import os
import random
import string
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from database import get_db_connection, init_db

load_dotenv()

app = FastAPI(
    title="Latha Oils E-Commerce API",
    description="Backend API and PostgreSQL Database service for Latha Oils Storefront",
    version="1.0.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed catalog for Latha Oils
SEED_PRODUCTS = [
    {
        "id": "groundnut-oil",
        "name": "Pure Wood Pressed Groundnut Oil",
        "category": "cooking",
        "tag": "Marachekku Special",
        "image": "assets/groundnut_oil.jpg",
        "description": "Extracted using traditional Vaagai wood cold press from selected Saurashtra & Tamil Nadu groundnuts. High smoke point and authentic nutty aroma.",
        "benefits": [
            "Rich in natural Vitamin E and heart-healthy MUFA",
            "Zero trans-fats, zero cholesterol, and no chemical argemone",
            "Traditional wood expeller ensures natural density and taste",
            "Ideal for deep frying, sautéing, and daily family cooking"
        ],
        "variants": [
            {"size": "500 ml", "price": 175, "originalPrice": 195},
            {"size": "1 Litre", "price": 340, "originalPrice": 380, "isDefault": True},
            {"size": "5 Litres (Tin)", "price": 1650, "originalPrice": 1850}
        ]
    },
    {
        "id": "coconut-oil",
        "name": "Pure Cold Pressed Coconut Oil",
        "category": "cooking",
        "tag": "100% Virgin Copra",
        "image": "assets/coconut_oil.jpg",
        "description": "Prepared from premium sulphur-free sun-dried copras of Pollachi. Unrefined, crystal-clear, with sweet natural coconut aroma.",
        "benefits": [
            "High concentration of Lauric acid for immunity",
            "Cold-extracted below 40°C preserving natural enzymes",
            "Multi-purpose: Ideal for cooking, raw consumption, and baby skin massage",
            "Zero artificial fragrance or bleaching chemicals"
        ],
        "variants": [
            {"size": "500 ml", "price": 190, "originalPrice": 220},
            {"size": "1 Litre", "price": 370, "originalPrice": 420, "isDefault": True},
            {"size": "5 Litres (Can)", "price": 1800, "originalPrice": 2000}
        ]
    },
    {
        "id": "gingelly-oil",
        "name": "Authentic Gingelly (Sesame) Oil",
        "category": "cooking",
        "tag": "Chekku Nallennai",
        "image": "assets/gingelly_oil.jpg",
        "description": "Cold-pressed with traditional palm jaggery (karupatti) to tame natural bitterness. Deep golden color, earthy aroma, and authentic South Indian taste.",
        "benefits": [
            "Traditional remedy for body heat regulation (Oil bath)",
            "Essential base for spicy gravies, puliyodharai, and idli milagai podi",
            "Packed with Sesamin, Sesamolin, and Zinc for bone strength",
            "Aids in natural blood pressure regulation"
        ],
        "variants": [
            {"size": "500 ml", "price": 210, "originalPrice": 245},
            {"size": "1 Litre", "price": 410, "originalPrice": 470, "isDefault": True},
            {"size": "5 Litres (Tin)", "price": 1980, "originalPrice": 2250}
        ]
    },
    {
        "id": "castor-oil",
        "name": "Cold-Pressed Castor Oil",
        "category": "wellness",
        "tag": "Hair & Skin Care",
        "image": "assets/castor_oil.jpg",
        "description": "Pure, thick, unrefined castor oil (Vilakkennai) extracted from selected ricinus seeds. Renowned for deep scalp moisturization and natural digestive balance.",
        "benefits": [
            "Stimulates hair follicle growth and prevents split ends",
            "Deeply hydrates dry skin, eyebrows, and cracked heels",
            "Traditional Ayurvedic remedy for cooling eyes and joints",
            "100% Hexane-free and unbleached"
        ],
        "variants": [
            {"size": "200 ml", "price": 110, "originalPrice": 130},
            {"size": "500 ml", "price": 240, "originalPrice": 275, "isDefault": True},
            {"size": "1 Litre", "price": 460, "originalPrice": 520}
        ]
    },
    {
        "id": "deepam-oil",
        "name": "Latha Sacred Deepam Pooja Oil",
        "category": "wellness",
        "tag": "Auspicious Fragrance",
        "image": "assets/deepam_oil.jpg",
        "description": "Inspired by temple traditions. A sacred blend of 5 pure oils (Gingelly, Mahua, Castor, Neem, Ghee extract) with mild Sugandh to bring positive spiritual vibrations.",
        "benefits": [
            "Burns long and steady with a clean, smokeless golden flame",
            "Leaves minimal carbon residue in brass & clay diyas",
            "Mild divine camphor and floral aroma creates peaceful meditation ambience",
            "Formulated according to Pancha Deepa sacred scriptural balance"
        ],
        "variants": [
            {"size": "500 ml", "price": 135, "originalPrice": 160},
            {"size": "1 Litre", "price": 260, "originalPrice": 300, "isDefault": True},
            {"size": "5 Litres (Jar)", "price": 1250, "originalPrice": 1450}
        ]
    },
    {
        "id": "neem-oil",
        "name": "Pure Organic Neem Oil",
        "category": "wellness",
        "tag": "Herbal & Organic",
        "image": "assets/neem_oil.jpg",
        "description": "100% pure cold-pressed oil from wild neem seeds (Azadirachta indica). Naturally high in Azadirachtin, perfect for therapeutic skin relief and organic garden pest care.",
        "benefits": [
            "Potent antibacterial and antifungal properties for acne & dandruff",
            "Natural organic repellent for home gardens and agriculture",
            "Helps treat eczema, insect bites, and scalp irritation",
            "Raw, unheated, with 100% active organic bio-compounds"
        ],
        "variants": [
            {"size": "200 ml", "price": 125, "originalPrice": 150},
            {"size": "500 ml", "price": 270, "originalPrice": 310, "isDefault": True},
            {"size": "1 Litre", "price": 510, "originalPrice": 580}
        ]
    },
    {
        "id": "raw-groundnut",
        "name": "Premium Raw Groundnut (Peanuts)",
        "category": "seeds",
        "tag": "Farm Fresh",
        "image": "https://images.unsplash.com/photo-1567894340315-735d7c361db0?auto=format&fit=crop&w=800&q=80",
        "description": "Hand-graded, plump, and naturally sun-dried peanuts directly from farms. Rich in oil content, sweet crunch, perfect for making homemade butter, snacks, or boiling.",
        "benefits": [
            "High plant protein (25g per 100g) and healthy dietary fiber",
            "Unpolished, chemical-free red-skin groundnuts",
            "Naturally dried under sunlight without sulfur processing",
            "Directly sourced from trusted local farming clusters"
        ],
        "variants": [
            {"size": "500 g", "price": 95, "originalPrice": 115},
            {"size": "1 kg", "price": 180, "originalPrice": 220, "isDefault": True},
            {"size": "5 kg (Bag)", "price": 850, "originalPrice": 990}
        ]
    },
    {
        "id": "sesame-seeds",
        "name": "Farm Fresh Natural Sesame Seeds",
        "category": "seeds",
        "tag": "Clean & Unpolished",
        "image": "https://images.unsplash.com/photo-1508737604135-49c377032e40?auto=format&fit=crop&w=800&q=80",
        "description": "Double machine-cleaned, 100% stone-free white and natural sesame seeds (Ellu). Perfect for making traditional sweets like ellu urundai, tahini, and bakery garnish.",
        "benefits": [
            "Exceptional natural source of plant calcium and iron",
            "Zero bleaching or artificial white polish",
            "Rich nutty flavor that pops when gently dry roasted",
            "Stored in climate-controlled hygiene packaging"
        ],
        "variants": [
            {"size": "250 g", "price": 80, "originalPrice": 95},
            {"size": "500 g", "price": 150, "originalPrice": 180, "isDefault": True},
            {"size": "1 kg", "price": 290, "originalPrice": 340}
        ]
    }
]

# Pydantic Models
class OrderItemCreate(BaseModel):
    productId: str
    name: str
    size: str
    price: float
    qty: int

class OrderCreate(BaseModel):
    customerName: str
    customerPhone: str
    customerEmail: Optional[str] = ""
    deliveryAddress: str
    city: str
    pincode: str
    paymentMethod: Optional[str] = "UPI / Online"
    items: List[OrderItemCreate]

@app.get("/")
def read_root():
    return {
        "service": "Latha Oils API",
        "status": "online",
        "docs": "/docs",
        "database": {
            "host": os.getenv("DB_HOST", "db.dttiqptqokirducezdyp.supabase.co"),
            "port": os.getenv("DB_PORT", "5432"),
            "database": os.getenv("DB_NAME", "postgres"),
            "user": os.getenv("DB_USER", "postgres")
        }
    }

@app.get("/api/health")
def health_check():
    """Verify API and Supabase PostgreSQL connectivity."""
    db_status = "connected"
    error_msg = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()["version"]
        conn.close()
    except Exception as e:
        db_status = "disconnected"
        error_msg = str(e)
        version = None

    return {
        "status": "ok",
        "database_status": db_status,
        "database_version": version,
        "error": error_msg
    }

@app.post("/api/init-db")
def initialize_database():
    """Create PostgreSQL tables in Supabase and populate default catalog."""
    try:
        result = init_db(SEED_PRODUCTS)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database initialization failed: {str(e)}"
        )

@app.get("/api/products")
def get_products():
    """Retrieve all products and variants from PostgreSQL."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM products ORDER BY id;")
            products = cur.fetchall()

            cur.execute("SELECT * FROM product_variants ORDER BY product_id, price ASC;")
            variants = cur.fetchall()
        conn.close()

        # Map variants to products
        variants_by_prod = {}
        for v in variants:
            p_id = v["product_id"]
            if p_id not in variants_by_prod:
                variants_by_prod[p_id] = []
            variants_by_prod[p_id].append({
                "size": v["size"],
                "price": float(v["price"]),
                "originalPrice": float(v["original_price"]) if v["original_price"] else None,
                "isDefault": v["is_default"]
            })

        for p in products:
            p["variants"] = variants_by_prod.get(p["id"], [])
            if isinstance(p.get("benefits"), str):
                import json
                p["benefits"] = json.loads(p["benefits"])

        return products
    except Exception as e:
        # Fallback to in-memory catalog if DB password is not configured yet
        print(f"[Notice] Using local fallback catalog: {e}")
        return SEED_PRODUCTS

@app.post("/api/orders", status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate):
    """Store customer order in Supabase PostgreSQL."""
    if not order.items:
        raise HTTPException(status_code=400, detail="Order items cannot be empty")

    total_amount = sum(item.price * item.qty for item in order.items)
    
    # Generate unique readable reference like LATHA-8492
    random_digits = ''.join(random.choices(string.digits, k=4))
    order_ref = f"LATHA-{random_digits}"

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO orders 
                (order_ref, customer_name, customer_phone, customer_email, delivery_address, city, pincode, payment_method, total_amount, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Confirmed')
                RETURNING id, order_ref, created_at;
            """, (
                order_ref,
                order.customerName,
                order.customerPhone,
                order.customerEmail,
                order.deliveryAddress,
                order.city,
                order.pincode,
                order.paymentMethod,
                total_amount
            ))
            new_order = cur.fetchone()
            order_id = new_order["id"]

            # Insert order items
            for item in order.items:
                cur.execute("""
                    INSERT INTO order_items 
                    (order_id, product_id, product_name, size, unit_price, quantity, total_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (
                    order_id,
                    item.productId,
                    item.name,
                    item.size,
                    item.price,
                    item.qty,
                    item.price * item.qty
                ))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "orderRef": order_ref,
            "totalAmount": total_amount,
            "message": "Order successfully recorded in Supabase database!"
        }
    except Exception as e:
        # If DB connection failed, record fallback order ID
        print(f"[Notice] Failed to write order to Supabase: {e}")
        return {
            "success": True,
            "orderRef": order_ref,
            "totalAmount": total_amount,
            "message": "Order accepted (fallback local mode). Configure DB_PASSWORD in .env for live Supabase sync.",
            "db_error": str(e)
        }

@app.get("/api/orders")
def get_orders():
    """Fetch recent orders from Supabase."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 50;")
            orders = cur.fetchall()
            
            cur.execute("SELECT * FROM order_items;")
            items = cur.fetchall()
        conn.close()

        items_by_order = {}
        for item in items:
            oid = item["order_id"]
            if oid not in items_by_order:
                items_by_order[oid] = []
            items_by_order[oid].append(item)

        for o in orders:
            o["items"] = items_by_order.get(o["id"], [])

        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
