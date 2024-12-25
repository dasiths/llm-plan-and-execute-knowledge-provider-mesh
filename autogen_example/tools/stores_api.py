from fastapi import FastAPI, HTTPException
from data import all_stores

stores_app = FastAPI(title="Stores API")

@stores_app.get("/stores")
async def get_all_stores():
    return all_stores

@stores_app.get("/stores/{store_id}")
async def find_store_by_id(store_id: str):
    store = next((store for store in all_stores if store["store_id"] == store_id), None)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store

@stores_app.get("/stores/closest")
async def find_closest_stores(location: str):
    # Simplified for now, returning all stores
    return {"message": f"Closest stores to {location} are:", "stores": all_stores}
