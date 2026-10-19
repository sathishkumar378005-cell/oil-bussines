# 🪔 Latha Oils — E-Commerce Storefront & Cloud Backend

A modern, high-performance full-stack e-commerce platform for **Latha Oils**, inspired by traditional cold-pressed edible oil brands like **Kaleesuwari**, powered by **FastAPI** and **Supabase PostgreSQL**.

---

## 🗄️ Database & Cloud Backend Integration

The backend is connected to your **Supabase PostgreSQL Database**:
* **Host:** `db.dttiqptqokirducezdyp.supabase.co`
* **Port:** `5432`
* **Database:** `postgres`
* **User:** `postgres`

### Database Tables:
1. `products` — Product ID, title, category, tag, image, description, and benefits JSON.
2. `product_variants` — Packaging sizes (500ml, 1L, 5L, 500g, 1kg), prices, and default flags.
3. `orders` — Customer contact info, delivery address, city, pincode, total amount, payment method, order reference.
4. `order_items` — Foreign key relations to orders storing purchased items, pack sizes, and prices.

---

## 📦 Products in Catalog

| Category | Product | Key Variants | Features |
| :--- | :--- | :--- | :--- |
| **Cooking Oils** | **Groundnut Oil** | 500ml, 1L, 5L Tin | Marachekku cold-pressed, high smoke point |
| **Cooking Oils** | **Coconut Oil** | 500ml, 1L, 5L Can | 100% Virgin sun-dried copra |
| **Cooking Oils** | **Gingelly (Sesame) Oil** | 500ml, 1L, 5L Tin | Pressed with traditional palm jaggery |
| **Pooja & Wellness** | **Castor Oil** | 200ml, 500ml, 1L | Hair follicle & skin hydration |
| **Pooja & Wellness** | **Deepam Oil** | 500ml, 1L, 5L Jar | Panchadeepam sacred blend for diya lamps |
| **Pooja & Wellness** | **Neem Oil** | 200ml, 500ml, 1L | Organic cold-pressed herbal antibacterial |
| **Farm Seeds & Grains** | **Raw Groundnut** | 500g, 1kg, 5kg Bag | Handpicked, sun-dried protein-rich peanuts |
| **Farm Seeds & Grains** | **Sesame Seeds** | 250g, 500g, 1kg | Clean, unpolished white & natural Til (Ellu) |

---

## 🔑 Quick Setup: Add Your Supabase Password

1. Open the [`.env`](file:///C:/Users/Asus/.gemini/antigravity/scratch/latha-oils/.env) file located in the root of the project.
2. Update the `DB_PASSWORD` field with your actual Supabase database password:
   ```env
   DB_HOST=db.dttiqptqokirducezdyp.supabase.co
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=YOUR_ACTUAL_SUPABASE_PASSWORD
   PORT=8000
   ```

---

## 🚀 Running the Full-Stack Application

### 1. Start the FastAPI Backend & Connect to Supabase
```powershell
cd C:\Users\Asus\.gemini\antigravity\scratch\latha-oils
python run_server.py
```
* **API Home:** [http://localhost:8000](http://localhost:8000)
* **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Initialize/Seed Database Tables:** Visit [http://localhost:8000/api/init-db](http://localhost:8000/api/init-db) (via POST in Swagger docs)

### 2. Open the Frontend Storefront
* Simply double-click [index.html](file:///C:/Users/Asus/.gemini/antigravity/scratch/latha-oils/index.html), or run:
  ```powershell
  python -m http.server 8080
  ```
  And open [http://localhost:8080](http://localhost:8080).

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Check API health & Supabase PostgreSQL connection status |
| `POST` | `/api/init-db` | Creates tables (`products`, `orders`, etc.) and seeds products |
| `GET` | `/api/products` | Returns all 8 products with their pack size variants from DB |
| `POST` | `/api/orders` | Places a new order, stores items and generates order reference |
| `GET` | `/api/orders` | Lists recent orders with customer details and line items |

---

## ☁️ Cloud Deployment (AWS)

* **Backend:** Deploy `backend/main.py` to **AWS App Runner** or **AWS ECS Fargate**.
* **Frontend:** Deploy static files to **AWS S3 + CloudFront CDN** using the included [`terraform/main.tf`](file:///C:/Users/Asus/.gemini/antigravity/scratch/latha-oils/terraform/main.tf).
