"""main.py - console menu for MeloSing (prototype)."""

from rooms import (create_reservation, get_available_rooms, find_reservation,
                   cancel_reservation, MAX_PAX)
from menu import list_menu_items, add_addon
from billing import build_receipt, compute_bill
from storage import save_data, load_data

RESERVATIONS_FILE = "reservations.json"
RECEIPTS_FILE = "receipts.json"


def read_int(prompt):
    """Ask until the user types a whole number."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a whole number.")


def load_or_empty(filename):
    try:
        return load_data(filename)
    except ValueError as error:
        print(f"Warning: {error}. Starting with an empty list.")
        return []


def handle_create(reservations):
    name = input("Customer name: ")
    pax = read_int(f"Number of guests (1-{MAX_PAX}): ")
    try:
        rooms = get_available_rooms(reservations, pax)
        if not rooms:
            print("No available room fits this group right now.")
            return
        print("Available rooms:")
        for i, (room, low, high, rate) in enumerate(rooms, start=1):
            print(f"  {i}. {room} ({low}-{high} pax) - PHP {rate}/hr")
        choice = read_int("Choose a room number: ")
        if choice < 1 or choice > len(rooms):
            raise ValueError("Invalid room choice")
        hours = read_int("Hours to book (minimum 1): ")
        reservation = create_reservation(reservations, name, pax, rooms[choice - 1][0], hours)
    except ValueError as error:
        print(f"Could not create reservation: {error}")
        return
    save_data(RESERVATIONS_FILE, reservations)
    print(f"Reserved! Your reservation ID is {reservation['id']}.")


def handle_addons(reservations):
    try:
        reservation = find_reservation(reservations, input("Reservation ID: "))
        if reservation["status"] != "Reserved":
            raise ValueError(f"This reservation is {reservation['status']}")
        for number, (category, name, price) in enumerate(list_menu_items(), start=1):
            print(f"  {number:2}. [{category}] {name} - PHP {price}")
        item_number = read_int("Item number: ")
        qty = read_int("Quantity: ")
        add_addon(reservation, item_number, qty)
    except ValueError as error:
        print(f"Could not add item: {error}")
        return
    save_data(RESERVATIONS_FILE, reservations)
    print("Item added.")


def handle_view(reservations):
    if not reservations:
        print("No reservations yet.")
    for r in reservations:
        print(f"{r['id']} | {r['customer']} | {r['room']} | {r['hours']} hr | "
              f"{len(r['add_ons'])} add-on(s) | {r['status']}")


def handle_cancel(reservations):
    try:
        reservation = find_reservation(reservations, input("Reservation ID: "))
        cancel_reservation(reservation)
    except ValueError as error:
        print(f"Could not cancel: {error}")
        return
    save_data(RESERVATIONS_FILE, reservations)
    print("Reservation cancelled.")


def handle_billing(reservations, receipts):
    try:
        reservation = find_reservation(reservations, input("Reservation ID: "))
        if reservation["status"] != "Reserved":
            raise ValueError(f"This reservation is {reservation['status']}")
    except ValueError as error:
        print(f"Could not bill: {error}")
        return
    receipt = build_receipt(reservation)
    print(receipt)
    reservation["status"] = "Completed"
    receipts.append({"id": reservation["id"], "customer": reservation["customer"],
                     "total": compute_bill(reservation), "receipt": receipt})
    save_data(RESERVATIONS_FILE, reservations)
    save_data(RECEIPTS_FILE, receipts)
    print("Payment recorded. Room is now available.")


def main():
    reservations = load_or_empty(RESERVATIONS_FILE)
    receipts = load_or_empty(RECEIPTS_FILE)
    while True:
        print("\n=== MeloSing ===")
        print("1. Create reservation\n2. Add add-ons\n3. View reservations")
        print("4. Cancel reservation\n5. Complete and bill\n0. Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            handle_create(reservations)
        elif choice == "2":
            handle_addons(reservations)
        elif choice == "3":
            handle_view(reservations)
        elif choice == "4":
            handle_cancel(reservations)
        elif choice == "5":
            handle_billing(reservations, receipts)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
