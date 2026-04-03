import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ------------------ DB FUNCTION ------------------
import os
import mysql.connector

def get_db():
    return mysql.connector.connect(
        host=os.getenv("mysql.railway.internal"),
        user=os.getenv("root"),
        password=os.getenv("xjUDXMvTcxEqKrkWdFQghNYsGPpBFkTK"),
        database=os.getenv("railway"),
        port=int(os.getenv("3306"))
    )

# ------------------ CORS ------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ LOGIN ------------------
@app.post("/login")
def login(data: dict):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM admins WHERE username=%s AND password=%s",
        (data["username"], data["password"])
    )

    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return {"status": "success", "restaurant_id": user["restaurant_id"]}
    else:
        return {"status": "fail"}


# ------------------ RESTAURANT ------------------
@app.get("/restaurant/{restaurant_id}")
def get_restaurant(restaurant_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM restaurants WHERE id=%s",
        (restaurant_id,)
    )

    data = cursor.fetchone()
    cursor.close()
    conn.close()

    return data


# ------------------ MENU ------------------
@app.post("/add-menu")
def add_menu(data: dict):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO menu (restaurant_id, item_name, price, category, image) VALUES (%s,%s,%s,%s,%s)",
        (
            data["restaurant_id"],
            data["name"],
            data["price"],
        data.get("category"),
        data.get("image")
    )
)

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "added"}


@app.get("/menu/{restaurant_id}")
def get_menu(restaurant_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
    "SELECT id, item_name as name, price, category, image FROM menu WHERE restaurant_id=%s",
    (restaurant_id,)
)

    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return data


@app.delete("/menu/{id}")
def delete_menu(id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM menu WHERE id=%s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "deleted"}


# ------------------ ORDERS ------------------
@app.post("/order")
def order(data: dict):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO orders (restaurant_id, table_no, customer_name, customer_address, items, total, status) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (
            data["restaurant_id"],
            data.get("table"),
            data.get("name"),
            data.get("address"),
            json.dumps(data["items"]),
            data["total"],
            "pending"
        )
    )

    conn.commit()
    order_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return {"message": "order placed", "order_id": order_id}


@app.get("/orders/{restaurant_id}")
def get_orders(restaurant_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM orders WHERE restaurant_id=%s ORDER BY id DESC",
        (restaurant_id,)
    )

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    for r in results:
        if isinstance(r["items"], str):
            r["items"] = json.loads(r["items"])

    return results


@app.put("/order/{id}")
def mark_done(id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE orders SET status='done' WHERE id=%s",
        (id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "updated"}


# ------------------ TEST ------------------
@app.get("/")
def home():
    return {"message": "API running"}