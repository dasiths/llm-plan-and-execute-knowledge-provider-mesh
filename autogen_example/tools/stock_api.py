from fastapi import FastAPI, HTTPException
from data import stock_qty

stock_app = FastAPI(title="Stock API")

@stock_app.get("/stock/{store_id}/{item_code}")
async def get_stock_level(store_id: str, item_code: str):
    stock = next((stock for stock in stock_qty if stock["store_id"] == store_id and stock["item_code"] == item_code), None)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {"qty": stock["qty"]}

@stock_app.get("/stock/available/{item_code}")
async def find_available_stock(item_code: str):
    available_stock = [stock for stock in stock_qty if stock["item_code"] == item_code and stock["qty"] > 0]
    if not available_stock:
        raise HTTPException(status_code=404, detail="No stock available")
    return available_stock
