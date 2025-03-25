from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from data import all_stores

class Store(BaseModel):
    store_id: str
    store_name: str
    address: str

stores_app = FastAPI(title="Stores API")

@stores_app.get("/stores/all", response_model=List[Store])
async def get_all_stores() -> List[Store]:
    return all_stores

@stores_app.get("/stores/store/{store_id}", response_model=Store)
async def find_store_by_id(store_id: str) -> Store:
    store = next((store for store in all_stores if store["store_id"] == store_id), None)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store

@stores_app.get("/stores/closest", response_model=List[Store])
async def find_closest_stores(location: str) -> List[Store]:
    return all_stores
