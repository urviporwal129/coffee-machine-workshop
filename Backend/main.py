# main.py
# ------------------------------------------------------
# Entry point of our backend.
# - Creates the database tables on startup
# - Serves the coffee menu (still a plain Python list — that's fine,
#   it's just a price catalog, not something we need to track stock for)
# - Saves every order into the database (orders + order_items tables)
#   instead of just calculating a total and forgetting it
# ------------------------------------------------------

from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import engine, Base, get_db
import models  # noqa: F401  (must be imported so SQLAlchemy knows about the tables)
import auth
from analytics import get_sales_summary, get_ingredient_report, check_coffee_availability

# Creates all tables in coffee.db if they don't already exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Coffee Machine API")

# Allow the frontend (running on a different port/origin) to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Coffee menu — just pricing/display info, unrelated to ingredient stock
menu = [
    {"id": 1, "name": "Espresso", "price": 40},
    {"id": 2, "name": "Latte", "price": 80},
    {"id": 3, "name": "Cappuccino", "price": 100},
    {"id": 4, "name": "Americano", "price": 90},
    {"id": 5, "name": "Cold Coffee", "price": 120},
    {"id": 6, "name": "Chocolate Coffee", "price": 150},
]


@app.get("/")
def home():
    return {"message": "Welcome to Sip & Spill!"}


@app.get("/menu")
def get_menu():
    return menu


@app.get("/menu/{coffee_id}")
def get_coffee(coffee_id: int):
    for coffee in menu:
        if coffee["id"] == coffee_id:
            return coffee
    return {"error": "Coffee not found"}


# ------------------------------------------------------
# Stock check — called by the frontend BEFORE adding to cart
# ------------------------------------------------------

class StockCheckRequest(BaseModel):
    coffee_id: int
    quantity: int  # total quantity being requested (existing cart + new)


@app.post("/check-stock")
def check_stock(request: StockCheckRequest, db: Session = Depends(get_db)):
    coffee = next((c for c in menu if c["id"] == request.coffee_id), None)
    if coffee is None:
        return {"error": "Coffee not found"}

    insufficient = check_coffee_availability(db, coffee["name"], request.quantity)

    return {
        "available": len(insufficient) == 0,
        "insufficient_ingredients": insufficient
    }


# ------------------------------------------------------
# Place an order
# ------------------------------------------------------

class OrderItemIn(BaseModel):
    coffee_id: int
    quantity: int


class OrderIn(BaseModel):
    items: List[OrderItemIn]


@app.post("/order")
def create_order(order: OrderIn, db: Session = Depends(get_db)):
    # Step 1: create the parent "orders" row first, so we get an id
    # to link every item to. We reuse that same id as the customer_number —
    # no manual entry needed, the database generates it for us.
    new_order = models.Order(customer_number=0)  # temporary placeholder
    db.add(new_order)
    db.commit()
    db.refresh(new_order)  # refresh() loads the auto-generated id back into new_order

    new_order.customer_number = new_order.id
    db.commit()

    total = 0
    order_items_response = []

    # Step 2: create one "order_items" row per coffee in the cart
    for item in order.items:
        coffee = next(
            (c for c in menu if c["id"] == item.coffee_id),
            None
        )
        if coffee is None:
            raise HTTPException(
                status_code=400,
                detail=f"Coffee with id {item.coffee_id} not found"
            )

        quantity = item.quantity
        item_total = coffee["price"] * quantity
        total += item_total

        db.add(models.OrderItem(
            order_id=new_order.id,
            coffee_name=coffee["name"],
            quantity=quantity
        ))

        order_items_response.append({
            "name": coffee["name"],
            "quantity": quantity,
            "price": coffee["price"],
            "total": item_total
        })

    db.commit()

    return {
        "message": "Order placed successfully!",
        "customer_number": new_order.customer_number,
        "items": order_items_response,
        "total": total
    }


# ------------------------------------------------------
# Admin login
# ------------------------------------------------------

# Pydantic model = defines what shape of JSON we expect in the request body.
# FastAPI automatically validates incoming requests against this.
class LoginRequest(BaseModel):
    passcode: str


class RestockIn(BaseModel):
    amount: float


@app.post("/admin/login")
def admin_login(credentials: LoginRequest):
    if not auth.check_passcode(credentials.passcode):
        # 401 = "Unauthorized" — the standard HTTP status for "wrong credentials"
        raise HTTPException(status_code=401, detail="Incorrect passcode")

    token = auth.create_token()
    return {"token": token}


# ------------------------------------------------------
# Admin dashboard (protected)
# ------------------------------------------------------

@app.get("/admin/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    admin: str = Depends(auth.get_current_admin),  # this line enforces the login check
):
    return {
        "sales": get_sales_summary(db),
        "ingredients": get_ingredient_report(db),
    }


# ------------------------------------------------------
# Restock ingredient (protected)
# ------------------------------------------------------

@app.post("/admin/ingredients/{ingredient_id}/restock")
def restock_ingredient(
    ingredient_id: int,
    restock: RestockIn,
    db: Session = Depends(get_db),
    admin: str = Depends(auth.get_current_admin),
):
    ingredient = db.query(models.Ingredient).filter(
        models.Ingredient.id == ingredient_id
    ).first()

    if ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    if restock.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    ingredient.initial_quantity += restock.amount
    db.commit()
    db.refresh(ingredient)

    return {
        "id": ingredient.id,
        "name": ingredient.name,
        "new_total": ingredient.initial_quantity,
        "unit": ingredient.unit
    }