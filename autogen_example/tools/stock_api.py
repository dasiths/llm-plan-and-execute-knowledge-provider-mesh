from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from data import stock_qty

class StockItem(BaseModel):
    store_id: str
    item_code: str
    qty: int

stock_app = FastAPI(title="Stock API")

@stock_app.get("/stock/{store_id}/{item_code}", response_model=StockItem)
async def get_stock_level(store_id: str, item_code: str) -> StockItem:
    stock = next((stock for stock in stock_qty if stock["store_id"] == store_id and stock["item_code"] == item_code), None)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@stock_app.get("/stock/available/{item_code}", response_model=List[StockItem])
async def find_available_stock(item_code: str) -> List[StockItem]:
    available_stock = [stock for stock in stock_qty if stock["item_code"] == item_code and stock["qty"] > 0]
    if not available_stock:
        raise HTTPException(status_code=404, detail="No stock available")
    return available_stock