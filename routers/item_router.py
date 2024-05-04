from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from models.Item import Item 
from init_db import get_db_conn

router = APIRouter()

@router.post("/items", response_model=Item)
def create_item(item: Item, conn: sqlite3.Connection = Depends(get_db_conn)):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)",
                   (item.name, item.price))
    conn.commit()
    return item

@router.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int, conn: sqlite3.Connection = Depends(get_db_conn)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item_data = cursor.fetchone()
    if not item_data:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item(name=item_data[1], price=item_data[2])

@router.delete("/items/{item_id}")
def delete_item(item_id: int, conn: sqlite3.Connection = Depends(get_db_conn)):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    return {"message": "Item deleted successfully"}

@router.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: Item, conn: sqlite3.Connection = Depends(get_db_conn)):
    cursor = conn.cursor()
    
    # First, check if the item exists
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    existing_item = cursor.fetchone()
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # If the item exists, perform the update
    cursor.execute("UPDATE items SET name = ?, price = ? WHERE id = ?",
                   (item.name, item.price, item_id))
    conn.commit()

    # Optionally, retrieve the updated item to return it
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    updated_item = cursor.fetchone()
    if not updated_item:
        raise HTTPException(status_code=404, detail="Error retrieving updated item")

    
    return Item(name=updated_item[1], price=updated_item[2])