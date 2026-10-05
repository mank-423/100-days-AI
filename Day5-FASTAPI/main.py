import time
from fastapi import FastAPI, Query, Request
from enum import Enum
from pydantic import BaseModel, Field
from typing import Annotated, Literal
from routers.user import router as user_router
from routers.stream import router as stream_router

app = FastAPI()

app.include_router(user_router) 
app.include_router(stream_router) 

# For resticting to the enum values
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

# Payload structure
class Item(BaseModel):
    name: str
    price: float
    tax: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }
    }

# Query Params model
class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


#Declaring middlewares
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/")
async def root():
    return {
        "message": "Hello world"
    }


# @app.get("/items")
# async def getItemsList(skip: int = 0, limit: int = 10):
#     return fake_items_db[skip: limit + skip]

@app.get("/items")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

@app.get("/items/me")
async def meItem():
    # await asyncio.sleep(10)
    return {"me": "item"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/models/{model_name}")
async def modelName(model_name: ModelName):
    return {
        "name": model_name
    }


@app.post("/")
async def showItems(payload: Item):
    return payload;