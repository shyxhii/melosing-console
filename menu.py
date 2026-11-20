"""menu.py - add-ons catalog and ordering (SUBSYSTEM 1)."""

# Dictionary of dictionaries: category -> {item name: price in PHP}
MENU = {
    "Food": {
        "Chips": 80,
        "Fried Chicken": 250,
        "Fries": 100,
        "Nachos": 150,
        "Pizza": 350,
        "Burger": 180,
    },
    "Drinks": {
        "Water - Cold": 30,
        "Water - Hot": 30,
        "Soda": 60,
        "Juice": 70,
        "Iced Tea": 70,
        "Hot Tea": 60,
        "Boba Tea": 120,
        "Beer": 90,
        "Soju": 180,
    },
    "Items": {
        "Tissues": 20,
        "Wet Wipes": 20,
        "Extra Microphone": 50,
    },
}


def list_menu_items():
    """Return a flat list of (category, name, price) so items can be numbered."""
    return [
        (category, name, price)
        for category, items in MENU.items()
        for name, price in items.items()
    ]


def add_addon(reservation, item_number, qty):
    """Add the numbered menu item to a reservation's add_ons list."""
    items = list_menu_items()
    if item_number < 1 or item_number > len(items):
        raise ValueError("Menu item not found")
    if qty < 1:
        raise ValueError("Quantity must be at least 1")
    if reservation["status"] != "Reserved":
        raise ValueError(f"Cannot add items to a {reservation['status']} reservation")

    _, name, price = items[item_number - 1]
    reservation["add_ons"].append({"item": name, "qty": qty, "price": price})
