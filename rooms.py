"""rooms.py - room constants and reservation logic (MAIN SYSTEM)."""

# Tuples: fixed values that do not change while the program runs.
# Each room is (name, min_pax, max_pax, hourly_rate)
ROOMS = (
    ("Duet", 1, 2, 120),
    ("Quartet", 3, 4, 200),
    ("Choir", 5, 8, 350),
    ("Concert", 15, 20, 800),
)
STATUSES = ("Reserved", "Completed", "Cancelled")
MAX_PAX = 20


def get_room(room_name):
    """Return the room tuple matching room_name, or raise ValueError."""
    for room in ROOMS:
        if room[0].lower() == room_name.strip().lower():
            return room
    raise ValueError(f"Room '{room_name}' not found")


def is_room_available(reservations, room_name):
    """A room is unavailable while it has a reservation with status 'Reserved'."""
    return not any(
        r["room"] == room_name and r["status"] == "Reserved" for r in reservations
    )


def get_available_rooms(reservations, pax):
    """Return the free rooms that can fit pax people (excess is not allowed)."""
    if pax < 1 or pax > MAX_PAX:
        raise ValueError(f"Number of guests must be between 1 and {MAX_PAX}")
    return [
        room for room in ROOMS
        if pax <= room[2] and is_room_available(reservations, room[0])
    ]


def create_reservation(reservations, name, pax, room_name, hours):
    """Validate the details and add a new reservation dictionary to the list."""
    if not name.strip():
        raise ValueError("Customer name is required")
    if hours < 1:
        raise ValueError("Minimum booking is 1 hour")
    room = get_room(room_name)
    if pax < 1 or pax > room[2]:
        raise ValueError(f"{room[0]} fits at most {room[2]} guests")
    if not is_room_available(reservations, room[0]):
        raise ValueError(f"{room[0]} is not available")

    reservation = {
        "id": f"R{len(reservations) + 1:03d}",
        "customer": name.strip(),
        "pax": pax,
        "room": room[0],
        "hours": hours,
        "add_ons": [],
        "status": "Reserved",
    }
    reservations.append(reservation)
    return reservation


def find_reservation(reservations, reservation_id):
    """Return the reservation with the given ID, or raise ValueError."""
    for r in reservations:
        if r["id"].lower() == reservation_id.strip().lower():
            return r
    raise ValueError(f"Reservation '{reservation_id}' not found")


def cancel_reservation(reservation):
    """Cancel a reservation that is still 'Reserved'."""
    if reservation["status"] != "Reserved":
        raise ValueError(f"Cannot cancel a {reservation['status']} reservation")
    reservation["status"] = "Cancelled"
