MENU = {

    "espresso": {
        "ingredients": {
            "water": 50,
            "milk": 0,
            "coffee": 18,
            "chocolate": 0
        },
        "cost": 40
    },

    "latte": {
        "ingredients": {
            "water": 200,
            "milk": 150,
            "coffee": 24,
            "chocolate": 0
        },
        "cost": 80
    },

    "cappuccino": {
        "ingredients": {
            "water": 250,
            "milk": 100,
            "coffee": 24,
            "chocolate": 0
        },
        "cost": 100
    }
}

resources = {
    "water": 1500,
    "milk": 1000,
    "coffee": 500,
    "chocolate": 200
}

money_box = 0

coffee_sales = {
    "espresso": 0,
    "latte": 0,
    "cappuccino": 0
}


def check_ingredients(drink):

    for item in MENU[drink]["ingredients"]:

        required = MENU[drink]["ingredients"][item]

        if resources[item] < required:
            return False

    return True


def make_coffee(drink):

    global money_box

    for item in MENU[drink]["ingredients"]:
        resources[item] -= MENU[drink]["ingredients"][item]

    coffee_sales[drink] += 1

    money_box += MENU[drink]["cost"]

    return f"{drink} prepared successfully"


def get_report():

    return {
        "water": resources["water"],
        "milk": resources["milk"],
        "coffee": resources["coffee"],
        "chocolate": resources["chocolate"],
        "money": money_box
    }