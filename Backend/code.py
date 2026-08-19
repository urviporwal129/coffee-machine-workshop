import matplotlib.pyplot as plt

# Coffee Menu
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
    },

    "americano": {
        "ingredients": {
            "water": 300,
            "milk": 0,
            "coffee": 20,
            "chocolate": 0
        },
        "cost": 90
    },

    "cold coffee": {
        "ingredients": {
            "water": 100,
            "milk": 200,
            "coffee": 20,
            "chocolate": 0
        },
        "cost": 120
    },

    "chocolate coffee": {
        "ingredients": {
            "water": 100,
            "milk": 150,
            "coffee": 20,
            "chocolate": 30
        },
        "cost": 150
    }
}

# Machine Resources
resources = {
    "water": 1500,
    "milk": 1000,
    "coffee": 500,
    "chocolate": 200
}

# Money Storage
money_box = 0

# Coffee Sales Counter
coffee_sales = {
    "espresso": 0,
    "latte": 0,
    "cappuccino": 0,
    "americano": 0,
    "cold coffee": 0,
    "chocolate coffee": 0
}


# Check Ingredients
def check_ingredients(drink):

    for item in MENU[drink]["ingredients"]:

        required = MENU[drink]["ingredients"][item]

        if resources[item] < required:
            print(f"\n❌ No sufficient {item} available.\n")
            return False

    return True


# Payment Function
def process_payment(drink):

    global money_box

    cost = MENU[drink]["cost"]

    print(f"\n💵 Cost = ₹{cost}")

    amount = int(input("Enter money: ₹"))

    if amount < cost:
        print("❌ Insufficient money. Refunded.\n")
        return False

    change = amount - cost

    if change > 0:
        print(f"💰 Change returned: ₹{change}")

    money_box += cost
    return True


# Make Coffee
def make_coffee(drink):

    for item in MENU[drink]["ingredients"]:
        resources[item] -= MENU[drink]["ingredients"][item]

    coffee_sales[drink] += 1

    print(f"\n☕ Your {drink} is ready! Enjoy!\n")


# Machine Report
def show_report():

    print("\n========== MACHINE REPORT ==========")
    print(f"Water      : {resources['water']} ml")
    print(f"Milk       : {resources['milk']} ml")
    print(f"Coffee     : {resources['coffee']} g")
    print(f"Chocolate  : {resources['chocolate']} g")
    print(f"Money Box  : ₹{money_box}")
    print("====================================\n")


# Sales Pie Chart
def show_sales_chart():

    labels = []
    sizes = []

    for coffee, count in coffee_sales.items():
        if count > 0:
            labels.append(coffee)
            sizes.append(count)

    if sum(sizes) == 0:
        print("\nNo coffees sold today.")
        return

    plt.figure(figsize=(8, 8))

    plt.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%"
    )

    plt.title("Coffee Sales Distribution")
    plt.legend(title="Coffee Types")
    plt.show()


# Main Program
while True:

    print("========= COFFEE MACHINE =========")
    print("1. Espresso          - ₹40")
    print("2. Latte             - ₹80")
    print("3. Cappuccino        - ₹100")
    print("4. Americano         - ₹90")
    print("5. Cold Coffee       - ₹120")
    print("6. Chocolate Coffee  - ₹150")
    print("7. Report")
    print("8. Exit")

    choice = input("\nChoose your coffee: ").lower()

    if choice == "1" or choice == "espresso":
        drink = "espresso"

    elif choice == "2" or choice == "latte":
        drink = "latte"

    elif choice == "3" or choice == "cappuccino":
        drink = "cappuccino"

    elif choice == "4" or choice == "americano":
        drink = "americano"

    elif choice == "5" or choice == "cold coffee":
        drink = "cold coffee"

    elif choice == "6" or choice == "chocolate coffee":
        drink = "chocolate coffee"

    elif choice == "7" or choice == "report":
        show_report()
        continue

    elif choice == "8" or choice == "exit":

        print("\n👋 Coffee Machine Shutting Down...")

        show_sales_chart()

        break

    else:
        print("\n❌ Invalid Choice\n")
        continue

    if check_ingredients(drink):

        if process_payment(drink):

            make_coffee(drink)