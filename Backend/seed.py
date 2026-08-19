# seed.py
# ------------------------------------------------------
# Run this file ONCE to fill the database with:
#   1. Starting ingredient stock (ingredients table)
#   2. Each coffee's recipe (recipes table)
#
# It's safe to run more than once — it checks if data
# already exists first, so it won't create duplicates.
# ------------------------------------------------------

from database import SessionLocal, engine, Base
import models

# Make sure tables exist before we try to insert into them
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ------------------------------------------------------
# 1. Starting ingredients
# Quantities are stored in the SMALLEST unit (ml, g) to avoid
# decimal/rounding issues later. We'll divide by 1000 only
# when displaying "10 L" or "2 kg" on the admin report.
# ------------------------------------------------------

starting_ingredients = [
    {"name": "Milk",             "initial_quantity": 10000, "unit": "ml"},  # 10 L
    {"name": "Coffee",           "initial_quantity": 2000,  "unit": "g"},   # 2 kg
    {"name": "Water",            "initial_quantity": 20000, "unit": "ml"},  # 20 L
    {"name": "Sugar",            "initial_quantity": 3000,  "unit": "g"},   # 3 kg
    {"name": "Chocolate Powder", "initial_quantity": 1000,  "unit": "g"},   # 1 kg
]

# Only seed if the table is currently empty — prevents duplicate rows
# if you accidentally run this script twice.
if db.query(models.Ingredient).count() == 0:
    for item in starting_ingredients:
        db.add(models.Ingredient(**item))
    db.commit()
    print(f"Inserted {len(starting_ingredients)} ingredients.")
else:
    print("Ingredients already exist — skipped.")


# ------------------------------------------------------
# 2. Recipes
# One entry per (coffee, ingredient) pair.
# quantity_required uses the SAME unit as that ingredient
# (e.g. Milk is in ml, so 100 here means 100 ml).
#
# ADJUST THESE to match your actual recipes — these are
# reasonable starting values, not exact measurements.
# ------------------------------------------------------

recipes_by_coffee = {
    "Espresso": [
        ("Coffee", 20),
        ("Water", 30),
        ("Sugar", 5),
    ],
    "Latte": [
        ("Milk", 150),
        ("Coffee", 20),
        ("Water", 30),
        ("Sugar", 10),
    ],
    "Cappuccino": [
        ("Milk", 100),
        ("Coffee", 20),
        ("Water", 50),
        ("Sugar", 10),
    ],
    "Americano": [
        ("Coffee", 20),
        ("Water", 150),
        ("Sugar", 10),
    ],
    "Cold Coffee": [
        ("Milk", 150),
        ("Coffee", 20),
        ("Water", 20),
        ("Sugar", 15),
    ],
    "Chocolate Coffee": [
        ("Milk", 150),
        ("Coffee", 20),
        ("Water", 30),
        ("Sugar", 15),
        ("Chocolate Powder", 20),
    ],
}

if db.query(models.Recipe).count() == 0:
    # Build a quick lookup: ingredient name -> ingredient row (so we can get its id)
    ingredients_by_name = {
        ing.name: ing for ing in db.query(models.Ingredient).all()
    }

    recipe_count = 0
    for coffee_name, ingredient_list in recipes_by_coffee.items():
        for ingredient_name, quantity in ingredient_list:
            ingredient = ingredients_by_name[ingredient_name]
            db.add(models.Recipe(
                coffee_name=coffee_name,
                ingredient_id=ingredient.id,
                quantity_required=quantity
            ))
            recipe_count += 1

    db.commit()
    print(f"Inserted {recipe_count} recipe rows.")
else:
    print("Recipes already exist — skipped.")

db.close()
print("Seeding complete.")