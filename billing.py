"""billing.py - bill computation and receipt (MAIN SYSTEM)."""

from rooms import get_room


def compute_bill(reservation):
    """Return total = room fee (rate x hours) + sum of qty x price of add-ons."""
    rate = get_room(reservation["room"])[3]
    room_fee = rate * reservation["hours"]
    addons_total = sum(a["qty"] * a["price"] for a in reservation["add_ons"])
    return room_fee + addons_total


def build_receipt(reservation):
    """Return an itemized receipt as a string."""
    rate = get_room(reservation["room"])[3]
    lines = [
        "=" * 36,
        "        MeloSing - RECEIPT",
        "=" * 36,
        f"Reservation: {reservation['id']}",
        f"Customer   : {reservation['customer']}",
        f"Guests     : {reservation['pax']}",
        "-" * 36,
        f"{reservation['room']} room: {reservation['hours']} hr x {rate}"
        f" = {rate * reservation['hours']:.2f}",
    ]
    for a in reservation["add_ons"]:
        lines.append(f"{a['item']}: {a['qty']} x {a['price']} = {a['qty'] * a['price']:.2f}")
    lines += ["-" * 36, f"TOTAL: PHP {compute_bill(reservation):.2f}", "=" * 36]
    return "\n".join(lines)
