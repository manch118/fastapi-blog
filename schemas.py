# schemas.py
from pydantic import BaseModel
from typing import List

class PostSchema(BaseModel):
    title: str
    content: str
    id: int

    class Config:
        orm_mode = True  # Это нужно для преобразования объектов SQLAlchemy в Pydantic-схему

class Config:
        orm_mode = True
        
class PaginatedPosts(BaseModel):
    items: List[PostSchema]
    total: int
    page: int
    per_page: int
    pages: int


class Config:
    from_attributes = True