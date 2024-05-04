from fastapi import APIRouter, Depends, HTTPException
from typing import List
import sqlite3
from pydantic import BaseModel
from models.Order import Order
from models.Item import Item
from init_db import get_db_conn
import logging
router = APIRouter()
# Setting up logging
logger = logging.getLogger(__name__)
@router.post("/orders", response_model=Order)
@router.post("/orders", response_model=Order)
def create_order(order: Order, conn: sqlite3.Connection = Depends(get_db_conn)):
    cursor = conn.cursor()

    try:
        # Start a transaction
        with conn:
            # Check if the customer exists by name and phone number
            cursor.execute("SELECT id FROM customers WHERE name = ? AND phone = ?", (order.name, order.phone))
            existing_customer = cursor.fetchone()
            if existing_customer:
                customer_id = existing_customer[0]
            else:
                # If customer doesn't exist, add them to the customers table
                cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (order.name, order.phone))
                customer_id = cursor.lastrowid

            # Insert order details
            cursor.execute("INSERT INTO orders (timestamp, customer_id, notes) VALUES (?, ?, ?)",
                           (order.timestamp, customer_id, order.notes))
            order_id = cursor.lastrowid

            # Insert order items
            for item in order.items:
                # Check if the item name already exists in the items table
                cursor.execute("SELECT id FROM items WHERE name = ?", (item.name,))
                existing_item = cursor.fetchone()
                if existing_item:
                    # If the item already exists, reuse its ID
                    item_id = existing_item[0]
                else:
                    # If the item doesn't exist, insert it into the items table
                    cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)",
                                   (item.name, item.price))
                    # Get the ID of the newly inserted item
                    item_id = cursor.lastrowid

                # Insert the item into the order_items table
                cursor.execute("INSERT INTO order_items (order_id, item_id) VALUES (?, ?)",
                               (order_id, item_id))

        # Commit the transaction
        conn.commit()

    except sqlite3.Error as e:
        # Rollback the transaction if an error occurs
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create order: {e}")

    return order

@router.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int, conn: sqlite3.Connection = Depends(get_db_conn)):
    cursor = conn.cursor()
    logger.info(f"Successfully retrieved order {order_id}")
    # Selecting order data along with customer information
    cursor.execute("""
        SELECT orders.id, orders.timestamp, orders.notes, customers.name, customers.phone, items.id, items.name, items.price
        FROM orders 
        INNER JOIN customers ON orders.customer_id = customers.id 
        INNER JOIN order_items ON orders.id = order_items.order_id
        INNER JOIN items ON order_items.item_id = items.id
        WHERE orders.id = ?
    """, (order_id,))
    order_data = cursor.fetchall()

    if not order_data:
        raise HTTPException(status_code=404, detail="Order not found")

    items = []
    for row in order_data:
        item_data = {
            "id": row[5],
            "name": row[6],
            "price": row[7]
        }
        items.append(Item(**item_data))


    # Creating an instance of the Order model with fetched data
    order = Order(
        id=order_data[0][0],
        timestamp=order_data[0][1],
        notes=order_data[0][2],
        name=order_data[0][3],  # Customer name
        phone=order_data[0][4],  # Customer phone
        items=items
    )
    return order

@router.delete("/orders/{order_id}")
def delete_order(order_id: int, conn: sqlite3.Connection = Depends(get_db_conn)):
    cursor = conn.cursor()

    # Delete associated records in order_items table
    cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))

    # Delete the order
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))

    conn.commit()
    return {"message": "Order deleted successfully"}


@router.put("/orders/{order_id}", response_model=Order)
def update_order(order_id: int, order: Order, conn: sqlite3.Connection = Depends(get_db_conn)):
    cursor = conn.cursor()

    # Check if the order exists
    cursor.execute("SELECT id FROM orders WHERE id = ?", (order_id,))
    existing_order = cursor.fetchone()
    if not existing_order:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        # Start a transaction
        with conn:
            # Update order details
            cursor.execute("UPDATE orders SET timestamp = ?, notes = ? WHERE id = ?",
                           (order.timestamp, order.notes, order_id))

            # Check if the provided customer name and phone exist in the customers table
            cursor.execute("SELECT id FROM customers WHERE name = ? AND phone = ?", (order.name, order.phone))
            existing_customer = cursor.fetchone()
            if existing_customer:
                # If customer exists, use their ID
                customer_id = existing_customer[0]
            else:
                # If customer doesn't exist, insert a new customer
                cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)",
                               (order.name, order.phone))
                # Get the ID of the newly inserted customer
                customer_id = cursor.lastrowid

            # Update customer_id associated with the order
            cursor.execute("UPDATE orders SET customer_id = ? WHERE id = ?", (customer_id, order_id))

            # Delete existing order items
            cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))

            # Insert updated order items
            for item in order.items:
                # Check if the item name already exists in the items table
                cursor.execute("SELECT id FROM items WHERE name = ?", (item.name,))
                existing_item = cursor.fetchone()
                if existing_item:
                    # If the item already exists, reuse its ID
                    item_id = existing_item[0]
                else:
                    # If the item doesn't exist, insert it into the items table
                    cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)",
                                   (item.name, item.price))
                    # Get the ID of the newly inserted item
                    item_id = cursor.lastrowid

                # Insert the item into the order_items table
                cursor.execute("INSERT INTO order_items (order_id, item_id) VALUES (?, ?)",
                               (order_id, item_id))

        # Commit the transaction
        conn.commit()

    except sqlite3.Error as e:
        # Rollback the transaction if an error occurs
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update order: {e}")

    return order


