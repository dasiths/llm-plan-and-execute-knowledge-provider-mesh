import uvicorn
from multiprocessing import Process

def run_stores_api():
    uvicorn.run("stores_api:stores_app", host="0.0.0.0", port=5000)

def run_catalog_api():
    uvicorn.run("catalog_api:catalog_app", host="0.0.0.0", port=5001)

def run_stock_api():
    uvicorn.run("stock_api:stock_app", host="0.0.0.0", port=5002)

if __name__ == "__main__":
    p1 = Process(target=run_stores_api)
    p2 = Process(target=run_catalog_api)
    p3 = Process(target=run_stock_api)

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
