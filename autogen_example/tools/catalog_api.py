from fastapi import FastAPI, HTTPException
from data import catalog

catalog_app = FastAPI(title="Catalog API")

@catalog_app.get("/catalog")
async def get_catalog():
    return catalog

@catalog_app.get("/catalog/{item_code}")
async def get_item_description(item_code: str):
    item = next((item for item in catalog if item["item_code"] == item_code), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_description": item["item_description"]}
