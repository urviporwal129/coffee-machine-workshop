# ☕ Sip & Spill

A full-stack coffee ordering and inventory management system built as a learning project. Customers can browse a menu, place orders, and pay via UPI, while an admin dashboard tracks sales analytics and ingredient stock in real time.

## Features

### Customer-facing
- Browse a coffee menu with pricing
- Add items to cart with quantity selection
- **Live stock checking** — the app verifies enough ingredients are available before adding items to cart
- Review and edit cart (update quantities, remove items)
- UPI-based payment flow with QR code
- Order confirmation popup on successful payment

### Admin dashboard
- Passcode-protected login with token-based session auth
- **Sales analytics**: best seller, total coffees sold, total orders, and a pie chart breakdown by coffee type
- **Ingredient report**: starting stock, amount used, and remaining stock per ingredient — calculated on the fly from order history
- **Restock ingredients** directly from the dashboard, with the report updating immediately after

## Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — Python web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM
- SQLite — database

**Frontend**
- Vanilla HTML, CSS, and JavaScript (no framework/build step)
- [Chart.js](https://www.chartjs.org/) — sales pie chart

## Project Structure

```
coffee-machine-workshop/
├── main.py              # FastAPI app: routes for menu, orders, admin
├── database.py          # SQLAlchemy engine/session setup
├── models.py             # ORM models (Ingredient, Recipe, Order, OrderItem)
├── analytics.py           # Sales & ingredient report calculations
├── auth.py               # Admin passcode check & token auth
├── index.html            # Customer menu page
├── cart.html              # Cart page
├── payment.html            # Payment / checkout page
├── admin.html             # Admin login + dashboard
├── script.js              # Customer-facing frontend logic
├── admin.js               # Admin dashboard frontend logic
├── style.css               # Shared stylesheet
└── coffee.db               # SQLite database (created automatically on first run)
```

## Database Design

- **ingredients** — name, starting quantity, unit (ml/g)
- **recipes** — links each coffee to the ingredients (and amounts) it requires
- **orders** — one row per customer order
- **order_items** — one row per coffee within an order (supports multiple items per order)

Ingredient usage and remaining stock are computed on demand from `order_items` and `recipes`, rather than stored as a running total — this keeps the numbers always accurate and gives a full audit trail via order history.

## Getting Started

### Prerequisites
- Python 3.9+
- A way to serve static HTML files (e.g. the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) VS Code extension)

### Backend setup

```bash
# Install dependencies
pip install fastapi uvicorn sqlalchemy

# Run the server
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### Frontend setup

Open `index.html` with Live Server (or any static file server). The frontend expects the backend running at `http://127.0.0.1:8000` — update `API_BASE_URL` in `script.js` and `admin.js` if your backend runs elsewhere.

> **Note:** If using Live Server, add `**/*.db` to `liveServer.settings.ignoreFiles` in your VS Code settings. Otherwise, every order placed (which writes to `coffee.db`) will trigger an unwanted page auto-reload.

### First run

On first launch, the backend creates `coffee.db` and its tables automatically. You'll need to seed it with initial ingredients and coffee recipes — see the seed script (or manually insert rows) before placing orders.

## API Overview

| Endpoint | Method | Description |
|---|---|---|
| `/menu` | GET | List all coffees |
| `/check-stock` | POST | Check if enough ingredients exist for a requested quantity |
| `/order` | POST | Place an order |
| `/admin/login` | POST | Authenticate with passcode, returns a session token |
| `/admin/dashboard` | GET | Combined sales + ingredient data (requires token) |
| `/admin/ingredients/{id}/restock` | POST | Add stock to an ingredient (requires token) |

## Known Limitations

- Admin tokens are stored in-memory on the server — restarting the backend logs out all admin sessions
- No real payment gateway integration; the UPI flow is a static QR code with a manual "Payment Done" confirmation
- Single currency (₹) and no multi-location support

## Authors

Built by Urvi Porwal and Spoorthi GM as a personal learning project.