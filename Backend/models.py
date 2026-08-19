# models.py
# ------------------------------------------------------
# Each class below = one table in the database.
# This matches the design we agreed on:
#   ingredients, recipes, orders, order_items
# ------------------------------------------------------

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)       # e.g. "Milk"
    initial_quantity = Column(Float, nullable=False)         # e.g. 10000 (store in ml/g, not L/kg)
    unit = Column(String, nullable=False)                    # e.g. "ml", "g"

    # This lets us do ingredient.recipes to see every recipe that uses this ingredient
    recipes = relationship("Recipe", back_populates="ingredient")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    coffee_name = Column(String, nullable=False)              # e.g. "Cappuccino"
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    quantity_required = Column(Float, nullable=False)         # e.g. 100 (ml of milk per cup)

    # This lets us do recipe.ingredient to get the full Ingredient row (name, unit, etc.)
    ingredient = relationship("Ingredient", back_populates="recipes")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    # We don't need the customer to type this in — the database
    # auto-generates "id" for every new order, and we can just
    # show that as "Customer 1", "Customer 2", etc.
    customer_number = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # This lets us do order.items to see every coffee in this order
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    coffee_name = Column(String, nullable=False)               # e.g. "Cappuccino"
    quantity = Column(Integer, nullable=False)                 # e.g. 2

    # This lets us do order_item.order to get back to the parent Order row
    order = relationship("Order", back_populates="items")