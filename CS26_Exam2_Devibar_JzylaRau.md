# MeloSing: KTV Pre-Order, Room Add-On, and Billing System
## CS 26 - Exam 2 Technical Documentation

**Program type:** MeloSing: KTV Pre-Order, Room Add-On, and Billing System (console-based)


## 1. Program Overview
MeloSing is a Python console program for a KTV venue. It creates room reservations, add food, drinks, and small items to the reservation, view reservations as a list, cancel reservations, and complete the reservation with an itemized bill and receipt. The program demonstrates basic use of Python collections, reusable functions, modules, file handling, and exception handling.

## 2. Problem Description
Many KTV places handle reservations, orders and billing manually through phone calls and paper slips. Orders and extension requests are forgotten or recorded wrongly, bills are computed by hand and can contain mistakes, and paper receipts get lost. MeloSing addresses this by organizing and managing reservations, add-on orders, and billing in one program so totals are computed automatically and records are saved.

**Input:** Customer name, number of guests, room choice, hours booked, add-on item number and quantity, and reservation ID.
**Processing:** Validate entries, check which rooms fit the group and are free, add add-ons to the reservation, compute hourly `rate × hours + (quantity × price of each add-on)`, and update the reservation status.
**Output:** Booking confirmation with reservation ID, reservation list, itemized receipt, and saved `reservations.json` and `receipts.json` files

## 3. Objectives
1. Reserve an available room that fits the number of guests for a minimum of 1 hour.
2. Add food, drink or item add-ons (with quantities) to an existing reservation.
3. Calculate the total bill as `hourly rate × hours + sum of (quantity × price) of add-ons`.
4. Print an itemized receipt when a reservation is completed.
5. Save and reload reservations and receipts so they persist between runs.

## 4. Program Requirements and Features
The prototype supports creating reservations, adding food, drink and item add-ons, viewing and cancelling reservations, and completing a reservation with an itemized receipt. Reservations and receipts are saved to and loaded from JSON files using the standard-library `json` module. It assumes four rooms (Duet for 1–2 guests at PHP 120/hr, Quartet for 3–4 at PHP 200/hr, Choir for 5–8 at PHP 350/hr, and Concert for 15–20 at PHP 800/hr), a minimum booking of 1 hour, and placeholder menu prices. As limitations, the program is console-only; a room is unavailable while it has a Reserved reservation (there is no date or time scheduling yet); a group cannot exceed a room's maximum but may take a larger room, so groups of 9–14 can only use Concert; the minimum capacity is not enforced; and there is no payment processing. Planned enhancements that are not yet implemented are room extensions (+30 min or +1 hr), a customer transaction history view, date and time reservations with overlap checking, booking two rooms for one large group, staff/owner sales reports, and a GUI or online version.

## 5. Program Structure
```text
cs26/
├── main.py            # console menu and user interaction
├── rooms.py           # room constants, availability, reservations   (main system)
├── billing.py         # bill computation and receipt                 (main system)
├── menu.py            # add-ons catalog and ordering                 (subsystem 1)
├── storage.py         # JSON save/load                               (subsystem 2)
├── reservations.json  # created when a reservation is saved
└── receipts.json      # created when a bill is completed
```

- `main.py` shows the menu, reads input, handles errors and calls the other modules.
- `rooms.py` holds the `ROOMS` constant and the reservation logic.
- `billing.py` computes totals and builds the receipt text.
- `menu.py` holds the `MENU` dictionary and adds items to a reservation.
- `storage.py` reads and writes JSON files.

**Imports:**
```python
# main.py
from rooms import (create_reservation, get_available_rooms, find_reservation,
                   cancel_reservation, MAX_PAX)
from menu import list_menu_items, add_addon
from billing import build_receipt, compute_bill
from storage import save_data, load_data

# billing.py
from rooms import get_room
```
`billing.py` imports `get_room` so it can look up a room's hourly rate. Keeping logic in modules and input/output in `main.py` makes each function easier to test.

## 6. Data Structures Used

### Tuple
Stores fixed room data while the program runs, so each room is an immutable tuple `(name, min_pax, max_pax, hourly_rate)`:

```python
ROOMS = (
    ("Duet", 1, 2, 120),
    ("Quartet", 3, 4, 200),
    ("Choir", 5, 8, 350),
    ("Concert", 15, 20, 800),
)
```

### Dictionary
Each reservation is a dictionary, so fields are accessed by name (`reservation["hours"]`). The menu is also a dictionary of `item name: price`, grouped by category:

```python
reservation = {
    "id": "R001", "customer": "trial", "pax": 2, "room": "Choir",
    "hours": 1, "add_ons": [], "status": "Reserved",
}
MENU = {"Food": {"Chips": 80, "Fried Chicken": 250}, "Drinks": {"Boba Tea": 120}}  # shortened
```

### List
Stores reservations and add-ons in a collection that grows over time. The following are lists:

```python
reservations.append(reservation)
reservation["add_ons"].append({"item": name, "qty": qty, "price": price})
```

## 7. Functions and Responsibilities

| Function | Parameters | Returns | Responsibility |
|---|---|---|---|
| `get_room` | `room_name` | room tuple | Find a room by name, or raise `ValueError` |
| `is_room_available` | `reservations`, `room_name` | `bool` | True if the room has no `Reserved` reservation |
| `get_available_rooms` | `reservations`, `pax` | list of rooms | Free rooms whose maximum fits the group |
| `create_reservation` | `reservations`, `name`, `pax`, `room_name`, `hours` | dict | Validate and add a reservation |
| `find_reservation` | `reservations`, `reservation_id` | dict | Look up a reservation, or raise `ValueError` |
| `cancel_reservation` | `reservation` | `None` | Set status to `Cancelled` |
| `list_menu_items` | none | list of tuples | Flatten the menu into numbered `(category, name, price)` items |
| `add_addon` | `reservation`, `item_number`, `qty` | `None` | Add a menu item to a reservation |
| `compute_bill` | `reservation` | number | Room fee + add-ons total |
| `build_receipt` | `reservation` | `str` | Itemized receipt text |
| `save_data` / `load_data` | `filename`, `data` / `filename` | `None` / list | JSON write / read |
| `read_int` | `prompt` | `int` | Ask until a whole number is typed |

**Excerpt 1 – computing the bill (`billing.py`)**
```python
def compute_bill(reservation):
    rate = get_room(reservation["room"])[3]
    room_fee = rate * reservation["hours"]
    addons_total = sum(a["qty"] * a["price"] for a in reservation["add_ons"])
    return room_fee + addons_total
```
It gets the hourly rate from the room tuple (index 3), multiplies by the hours, then sums quantity × price for every add-on dictionary in the list.

**Excerpt 2 – finding rooms for a group (`rooms.py`)**
```python
def get_available_rooms(reservations, pax):
    if pax < 1 or pax > MAX_PAX:
        raise ValueError(f"Number of guests must be between 1 and {MAX_PAX}")
    return [
        room for room in ROOMS
        if pax <= room[2] and is_room_available(reservations, room[0])
    ]
```
It rejects an invalid group size, then keeps only rooms whose maximum capacity (index 2) fits the group and which are free.

## 8. File Handling Procedures
Two JSON files are used: `reservations.json` (all reservations) and `receipts.json` (one record per completed bill: ID, customer, total and receipt text). JSON is used because it stores Python lists and dictionaries directly.

```python
def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

def load_data(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            records = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        raise ValueError(f"{filename} is corrupted")
    if not isinstance(records, list):
        raise ValueError(f"{filename} has an invalid format")
    return records
```
- **`"w"`** creates or replaces the file when saving; **`"r"`** reads it when loading.
- **`with open(...)`** closes the file automatically, even if an error occurs.
- **Missing file:** `load_data` returns an empty list, so the first run starts with no records.
- **Malformed file:** the error is raised as `ValueError`. `main.py` catches it, prints a warning and starts with an empty list.
- **Persistence:** yes. Data is saved after every create, add-on, cancel and bill, and loaded at startup (Test T6).
- **Limitation:** after a corrupted-file warning, the next save overwrites the corrupted file with the new empty data. The file paths are relative, so the files are saved in the folder the program is run from (see Debugging).

## 9. Error Handling
**Input-validation errors (expected).** These are raised as `ValueError` by the functions and caught where a helpful message can be shown:

```python
def read_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a whole number.")
```
```python
try:
    reservation = find_reservation(reservations, input("Reservation ID: "))
    ...
except ValueError as error:
    print(f"Could not bill: {error}")
    return
```
Handled cases: non-numeric input, guests outside 1–20, hours below 1, quantity below 1, invalid room or menu number, unknown reservation ID, billing/adding items/cancelling a reservation that is not `Reserved`, an unavailable room, a missing file, and a corrupted file.

**Unexpected programming errors.** The program does not use a bare `except:`. Only `ValueError` (and `FileNotFoundError`/`JSONDecodeError` inside `load_data`) are caught, so a real bug shows its traceback instead of being hidden.

## 10. Testing, Debugging, and Results
Tests were run by the student in the console. T1–T6 were run in one session; T7–T10 were run afterwards from the project folder.

| ID | Scenario | Input | Expected result | Actual result | Status |
|---|---|---|---|---|---|
| T1 | Normal: reserve, add-on, bill (1 hour is the minimum) | Name `test1`, 2 guests, room 1 (Duet), 1 hr; add item 16 (Tissues) × 2; bill `R001` | Total = 120 + 40 = PHP 160.00 | Receipt: Duet 1 hr × 120 = 120.00, Tissues 2 × 20 = 40.00, **TOTAL PHP 160.00**; "Payment recorded. Room is now available." | Pass |
| T2 | Group larger than the smaller rooms | Name `TEST2`, 9 guests, room 1, 1 hr | Only Concert is offered | Only "1. Concert (15–20 pax)" listed; reservation R002 created | Pass |
| T3 | Boundary / unavailable: maximum group size while Concert is reserved | Name `TEST3UNAVROOM`, 20 guests | No room offered | "No available room fits this group right now." | Pass |
| T4 | Invalid input: hours as text | 4 guests, room 1 (Quartet), hours `ONE`, then `1` | Error message, then asks again | "Please enter a whole number." then accepted `1`; R003 created | Pass |
| T5 | Cancel a reservation | Option 4, `R003` | Reservation cancelled | "Reservation cancelled." | Pass |
| T6 | Persistence between runs | Exit (0), run again, option 3 | Records still listed | R001 Completed, R002 Reserved, R003 Cancelled | Pass |
| T7 | Missing file | No `reservations.json`; option 3 | Empty list, no crash | "No reservations yet." | Pass |
| T8 | Corrupted file | Closing `]` deleted from `reservations.json`; run program | Warning, empty list | "Warning: reservations.json is corrupted. Starting with an empty list." | Pass |
| T9 | Boundary: guests just above maximum | Name `trial21`, 21 guests | Error message | "Could not create reservation: Number of guests must be between 1 and 20" | Pass |
| T10 | Unknown reservation ID | Option 5, `R067` | Error message | "Could not bill: Reservation 'R067' not found" | Pass |

### Debugging

**Issue:** On the first test run, the JSON files were not in the project folder `cs26`. The terminal was started in VS Code's default folder (`...\Microsoft VS Code>`) while `main.py` was stored elsewhere, yet records still persisted between runs.  
**Cause:** `RESERVATIONS_FILE` and `RECEIPTS_FILE` are relative paths (`"reservations.json"`), so Python saves them in the folder the program is *run from*, not the folder where `main.py` is stored.  
**Correction:** The project folder `cs26` was opened in VS Code and the program was run from there. No code was changed.  
**Verification:** After running from `cs26`, `reservations.json` appeared in the Explorer next to `main.py`, and T7–T10 were run from this folder.  
**Possible permanent fix (not applied):** build the file paths from the location of `main.py` so the folder does not matter.

## 11. Conclusion
The prototype lets a user reserve a suitable free room, add food, drinks and items, cancel, and complete a reservation with a computed itemized receipt. Reservations and receipts persist in JSON files, and invalid input, unavailable rooms and missing or corrupted files are handled without crashing. It demonstrates lists, tuples, dictionaries, functions, modules, file handling and error handling.

**Limitations:** availability has no date or time; the minimum group size is not enforced; a corrupted file is overwritten on the next save; the files are saved in the run folder.  
**Improvements:** add room extensions and a customer history view, then date/time reservations with overlap checking.

## 12. References
- Python Software Foundation. *Python 3 Tutorial: Data Structures*. https://docs.python.org/3/tutorial/datastructures.html
- Python Software Foundation. *Python 3 Tutorial: Errors and Exceptions*. https://docs.python.org/3/tutorial/errors.html
- Python Software Foundation. *Python 3 Tutorial: Reading and Writing Files*. https://docs.python.org/3/tutorial/inputoutput.html
- Python Software Foundation. *Python 3 Tutorial: Modules*. https://docs.python.org/3/tutorial/modules.html
- Python Software Foundation. *json module documentation*. https://docs.python.org/3/library/json.html
- Claude (an AI assistant by Anthropic) was consulted for guidance on program structure, sample code, and documentation wording. 

---