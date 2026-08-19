# analytics.py
# ------------------------------------------------------
# This file has no routes — just two plain Python functions
# that do the actual math. We keep this separate from main.py
# so it's easy to test on its own, and later the admin routes
# will just call these functions and return their result as JSON.
# ------------------------------------------------------

from sqlalchemy.orm import Session
from sqlalchemy import func

import models


def get_sales_summary(db: Session):
    """
    Groups all order_items by coffee_name and sums the quantities.
    Returns something like:
      {
        "sales_by_coffee": {"Cappuccino": 15, "Latte": 10, ...},
        "best_seller": "Cappuccino",
        "total_coffees_sold": 32,
        "total_orders": 12
      }
    """

    # This is the SQL equivalent of:
    #   SELECT coffee_name, SUM(quantity) FROM order_items GROUP BY coffee_name
    results = (
        db.query(
            models.OrderItem.coffee_name,
            func.sum(models.OrderItem.quantity).label("total_quantity")
        )
        .group_by(models.OrderItem.coffee_name)
        .all()
    )

    # `results` is a list of row objects like (coffee_name, total_quantity).
    # Turn it into a plain dictionary, e.g. {"Cappuccino": 15, "Latte": 10}
    sales_by_coffee = {row.coffee_name: row.total_quantity for row in results}

    if sales_by_coffee:
        best_seller = max(sales_by_coffee, key=sales_by_coffee.get)
    else:
        best_seller = None

    total_coffees_sold = sum(sales_by_coffee.values())
    total_orders = db.query(models.Order).count()

    return {
        "sales_by_coffee": sales_by_coffee,
        "best_seller": best_seller,
        "total_coffees_sold": total_coffees_sold,
        "total_orders": total_orders,
    }


def get_ingredient_report(db: Session):
    """
    For every ingredient, calculates how much has been used across
    ALL orders ever placed, and what's left.

    used = sum over every order_item of (quantity_ordered * quantity_required_per_cup)
           but only for recipes that use this ingredient

    Returns a list like:
      [
        {"name": "Milk", "starting": 10000, "used": 3000, "remaining": 7000, "unit": "ml"},
        ...
      ]
    """

    ingredients = db.query(models.Ingredient).all()
    report = []

    for ingredient in ingredients:

        # Find every recipe row that uses this ingredient
        # e.g. for Milk: [(Cappuccino, 100), (Latte, 150), ...]
        recipe_rows = (
            db.query(models.Recipe)
            .filter(models.Recipe.ingredient_id == ingredient.id)
            .all()
        )

        used = 0.0

        for recipe in recipe_rows:
            # How many of THIS coffee have been sold in total?
            total_sold = (
                db.query(func.sum(models.OrderItem.quantity))
                .filter(models.OrderItem.coffee_name == recipe.coffee_name)
                .scalar()  # .scalar() gets just the number, not a row object
            ) or 0  # if no orders yet, this would be None — treat as 0

            used += total_sold * recipe.quantity_required

        remaining = ingredient.initial_quantity - used

        report.append({
            "id": ingredient.id,
            "name": ingredient.name,
            "starting": ingredient.initial_quantity,
            "used": used,
            "remaining": remaining,
            "unit": ingredient.unit,
        })

    return report


def get_remaining_ingredients(db: Session):
    """
    Returns a simple dict of ingredient_name -> remaining quantity,
    reusing the same calculation as get_ingredient_report().
    e.g. {"Milk": 7000, "Coffee": 1500, ...}
    """
    report = get_ingredient_report(db)
    return {item["name"]: item["remaining"] for item in report}


def check_coffee_availability(db: Session, coffee_name: str, quantity: int):
    """
    Checks whether there's enough of EVERY ingredient to make
    `quantity` cups of `coffee_name`, given what's already been used
    by all previous orders.

    Returns a list of ingredient names that don't have enough stock.
    An empty list means everything needed is available.
    """
    remaining = get_remaining_ingredients(db)

    recipe_rows = (
        db.query(models.Recipe)
        .filter(models.Recipe.coffee_name == coffee_name)
        .all()
    )

    insufficient = []

    for recipe in recipe_rows:
        ingredient_name = recipe.ingredient.name
        needed = recipe.quantity_required * quantity
        available = remaining.get(ingredient_name, 0)

        if available < needed:
            insufficient.append(ingredient_name)

    return insufficient