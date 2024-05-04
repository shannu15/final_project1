from pydantic import BaseModel
from typing import List
from models.Item import Item

class Order(BaseModel):
    timestamp: int 
    name: str
    phone: str
    items: List[Item]
    notes: str  

