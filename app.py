from flask import Flask
from coffee_logic import *

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>☕ Coffee Machine</h1>

    <a href='/order/espresso'>Espresso</a><br><br>

    <a href='/order/latte'>Latte</a><br><br>

    <a href='/order/cappuccino'>Cappuccino</a><br><br>

    <a href='/report'>Report</a>
    """


@app.route("/order/<drink>")
def order(drink):

    if drink not in MENU:
        return "Invalid Coffee"

    if check_ingredients(drink):

        return make_coffee(drink)

    return "Not enough ingredients"


@app.route("/report")
def report():

    return get_report()


if __name__ == "__main__":
    app.run(debug=True)