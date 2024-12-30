from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from data import catalog

class CatalogItem(BaseModel):
    item_description: str
    item_code: str

catalog_app = FastAPI(title="Catalog API")

@catalog_app.get("/catalog", response_model=List[CatalogItem])
async def get_catalog() -> List[CatalogItem]:
    return catalog

@catalog_app.get("/catalog/{item_code}", response_model=CatalogItem)
async def get_item_description(item_code: str) -> CatalogItem:
    item = next((item for item in catalog if item["item_code"] == item_code), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
