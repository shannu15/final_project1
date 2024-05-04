import sqlite3
import json
from fastapi import FastAPI, Depends
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
# Dependency for database connection
def get_db_conn():
    conn = sqlite3.connect('db.sqlite')
    try:
        yield conn
    finally:
        conn.close()

@app.on_event("startup")
async def initialize_database():
    with get_db_conn() as conn:
        c = conn.cursor()
        
        # Drop existing tables if they exist
        c.execute("DROP TABLE IF EXISTS customers")
        c.execute("DROP TABLE IF EXISTS items")
        c.execute("DROP TABLE IF EXISTS orders")
        c.execute("DROP TABLE IF EXISTS order_items")
        
        # Create tables
        c.execute('''CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        phone TEXT
                    )''')

        c.execute('''CREATE TABLE IF NOT EXISTS items (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        price REAL
                    )''')

        c.execute('''CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY,
                        timestamp INTEGER,
                        customer_id INTEGER,
                        notes TEXT,
                        FOREIGN KEY (customer_id) REFERENCES customers(id)
                    )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS order_items (
                        order_id INTEGER,
                        item_id INTEGER,
                        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE ON UPDATE CASCADE,
                        FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE ON UPDATE CASCADE
                    )''')

        # Load data from example_orders.json
        with open('example_orders.json', 'r') as file:
            data = json.load(file)

        # Populate customers table
        for order in data:
            customer_name = order['name']
            phone = order['phone']
            
            # Check if customer already exists
            c.execute("SELECT id FROM customers WHERE name = ? AND phone = ?", (customer_name, phone))
            existing_customer = c.fetchone()
        
            if existing_customer:
                customer_id = existing_customer[0]
            else:
                # Insert new customer
                customer_id = c.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (customer_name, phone)).lastrowid

            # Populate orders table
            order_id = c.execute("INSERT INTO orders (timestamp, customer_id, notes) VALUES (?, ?, ?)", (order['timestamp'], customer_id, order['notes'])).lastrowid

            # Populate items and order_items tables
            for item in order['items']:
                item_name = item['name']
                item_price = item['price']
                
                # Check if item exists
                c.execute("SELECT id FROM items WHERE name = ?", (item_name,))
                existing_item = c.fetchone()
                
                if existing_item:
                    item_id = existing_item[0]  # ID of the existing item
                  
                    c.execute("INSERT INTO order_items (order_id, item_id) VALUES (?, ?)", (order_id, item_id))
                else:
                    
                    item_id = c.execute("INSERT INTO items (name, price) VALUES (?, ?)", (item_name, item_price)).lastrowid
                    c.execute("INSERT INTO order_items (order_id, item_id) VALUES (?, ?)", (order_id, item_id))
                    
                 
        # Commit changes
        conn.commit()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)