from pydantic import BaseModel

class Customer(BaseModel):
    name: str
    phone: str