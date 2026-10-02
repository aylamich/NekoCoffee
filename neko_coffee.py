"""
RA1 - Neko Cafe (=^.^=)  -  kawaii cat cafe

Business context: Neko Cafe is a cat cafe. Customers pay for the time
they spend with the resident kittens and can order snacks. The cafe must
take care of the cats' welfare, since they cannot receive visits
without rest.

Problem: calculate the value of each visit (time + snacks - package
discount), record the sales of the day and control which cats can
receive visits according to each cat's welfare (hunger, happiness,
energy).

Purpose: the attendant knows right away how much to charge and which
cat is available; the owner sees the daily revenue (total, number of
visits, average ticket, most visited cats) and whether any cat needs care.

IPO (Input -> Processing -> Output):
  Input:      customer name, chosen cat, visit minutes, snacks ordered,
              staff actions (feed, nap, register a cat) -> input()
  Processing: time value, package discount (if/elif/else), snacks total,
              visit total, cat status from energy (if/elif/else), effect
              of the visit on the cat, alerts and daily report
              (business functions with return)
  Output:     receipt formatted in R$, cat panel with bars and kaomojis,
              welfare alerts and daily report -> print()

How to run:  python neko_coffee.py
"""

# ==========================================================
# CONSTANTS (business rules)
# ==========================================================
INDICATOR_MIN = 0              # BR01: indicators go from 0 to 100
INDICATOR_MAX = 100

PRICE_PER_MINUTE = 0.50        # BR02: R$ 0,50 per minute of visit

MIN_MINUTES = 5                # BR10: visits from 5 to 120 minutes
MAX_MINUTES = 120

LONG_PACKAGE_MINUTES = 60      # BR04: >= 60 min -> 15% on the time value
LONG_PACKAGE_DISCOUNT = 0.15
MEDIUM_PACKAGE_MINUTES = 30    # BR04: >= 30 min -> 10% on the time value
MEDIUM_PACKAGE_DISCOUNT = 0.10

AVAILABLE_ENERGY = 40          # BR05: energy > 40 -> Available
TIRED_ENERGY = 15              # BR05: energy > 15 -> Tired, otherwise Resting
TIRED_MAX_MINUTES = 15         # BR05: a tired cat accepts at most 15 min
TIRED_CAT_DISCOUNT = 0.10      # BR11: short visit with a tired cat -> 10% courtesy

VISIT_HAPPINESS = 15           # BR06: a visit makes the cat +15 happier
VISIT_MINUTES_PER_ENERGY = 3   # BR06: -1 energy every 3 minutes
VISIT_HUNGER = 5               # BR06: a visit adds +5 hunger

CAT_TREAT = "Cat treat"        # BR07: a cat treat reduces the cat's hunger
CAT_TREAT_HUNGER = 20

FEED_HUNGER = 35               # BR08: feed -> hunger -35
NAP_ENERGY = 40                # BR08: nap -> energy +40

HUNGER_ALERT = 80              # BR09: hunger >= 80 -> alert
HAPPINESS_ALERT = 20           # BR09: happiness <= 20 -> alert
ENERGY_ALERT = 15              # BR09: energy <= 15 -> alert

STATUS_AVAILABLE = "Available"
STATUS_TIRED = "Tired"
STATUS_RESTING = "Resting"

# List: personality options when registering a cat
PERSONALITIES = ["Sleepy", "Playful", "Foodie", "Shy"]

# Dictionary: snack menu (snack name -> price in reais)
MENU = {
    "Matcha latte": 14.0,
    "Taiyaki": 9.5,
    "Onigiri": 8.0,
    CAT_TREAT: 6.0,
}

# Dictionary: ASCII kaomoji for each status
KAOMOJIS = {
    STATUS_AVAILABLE: "(=^.^=)",
    STATUS_TIRED: "(=-.-=)",
    STATUS_RESTING: "(=u.u=) zZ",
}


# ==========================================================
# BUSINESS FUNCTIONS (calculate and return; no input/print)
# ==========================================================

def clamp_indicator(value):
    """BR01: keeps an integer indicator between 0 and 100."""
    return max(INDICATOR_MIN, min(INDICATOR_MAX, int(value)))


def format_currency(value, width=0):
    """Formats in the Brazilian standard: 1234.5 -> 'R$ 1.234,50'.

    width right-aligns the number (for the receipt): 2.25, 6 -> 'R$   2,25'.
    """
    us_text = f"{value:,.2f}"                              # '1,234.50'
    brazilian_text = (us_text.replace(",", "_")
                      .replace(".", ",").replace("_", "."))
    return f"R$ {brazilian_text:>{width}}"


def calculate_time_value(minutes):
    """BR02: time value = minutes x price per minute."""
    return round(minutes * PRICE_PER_MINUTE, 2)            # calculation


def calculate_discount_rate(minutes):
    """BR04 (if/elif/else): discount rate from the time package."""
    if minutes >= LONG_PACKAGE_MINUTES:
        return LONG_PACKAGE_DISCOUNT
    elif minutes >= MEDIUM_PACKAGE_MINUTES:
        return MEDIUM_PACKAGE_DISCOUNT
    else:
        return 0.0


def calculate_visit_discount_rate(minutes, status):
    """BR04/BR11: a tired cat gives a 10% courtesy; otherwise the time package applies."""
    if status == STATUS_TIRED:
        return TIRED_CAT_DISCOUNT
    return calculate_discount_rate(minutes)


def describe_discount(status, rate):
    """Discount text on the receipt: 'Package discount (10%)' or 'Tired-cat courtesy (10%)'."""
    rate_text = f"{rate * 100:.0f}%"
    if status == STATUS_TIRED:
        return f"Tired-cat courtesy ({rate_text})"
    return f"Package discount ({rate_text})"


def calculate_discount(time_value, rate):
    """BR04: discount in reais on the time value (half a cent rounds up).

    The calculation uses whole cents because round() with float rounds
    half a cent inconsistently (4.575 -> 4.58, but 4.725 -> 4.72).
    """
    time_cents = round(time_value * 100)                   # conversion to cents
    rate_points = round(rate * 100)                        # 0.15 -> 15
    discount_cents = (time_cents * rate_points + 50) // 100  # calculation
    return discount_cents / 100


def calculate_snacks_value(snacks):
    """Adds up the prices of the snacks ordered (list of MENU names)."""
    snacks_value = 0.0
    for snack in snacks:
        snacks_value += MENU[snack]                        # calculation
    return round(snacks_value, 2)


def calculate_visit_total(time_value, discount, snacks_value):
    """BR03: total = time value - discount + snacks."""
    return round(time_value - discount + snacks_value, 2)  # calculation


def classify_cat_status(energy):
    """BR05 (if/elif/else): availability status from energy."""
    if energy > AVAILABLE_ENERGY:
        return STATUS_AVAILABLE
    elif energy > TIRED_ENERGY:
        return STATUS_TIRED
    else:
        return STATUS_RESTING


def calculate_allowed_minutes(status):
    """BR05/BR10 (if/elif/else): maximum minutes the cat accepts."""
    if status == STATUS_AVAILABLE:
        return MAX_MINUTES
    elif status == STATUS_TIRED:
        return TIRED_MAX_MINUTES
    else:
        return 0


def convert_to_int(text):
    """Converts text to int; returns None if it is not a whole number."""
    try:
        return int(text.strip())                           # type conversion
    except ValueError:
        return None


def validate_minutes(minutes, max_allowed):
    """BR10: valid minutes are integers between 5 and the maximum allowed."""
    if minutes is None:
        return False
    return MIN_MINUTES <= minutes <= max_allowed


def create_cat(name, personality):
    """Creates the dictionary that represents one resident kitten."""
    return {
        "name": name,
        "personality": personality,
        "hunger": 30,
        "happiness": 70,
        "energy": 80,
        "visits_today": 0,
        "history": [],
    }


def find_cat(cats, name):
    """Finds a cat by name (case-insensitive). None if not found."""
    for cat in cats:
        if cat["name"].lower() == name.strip().lower():
            return cat
    return None


def apply_visit_effect(cat, minutes, snacks):
    """BR06/BR07: updates the cat's hunger, happiness and energy after the visit."""
    energy_spent = minutes // VISIT_MINUTES_PER_ENERGY            # calculation
    cat["happiness"] = clamp_indicator(cat["happiness"] + VISIT_HAPPINESS)
    cat["energy"] = clamp_indicator(cat["energy"] - energy_spent)
    cat["hunger"] = clamp_indicator(cat["hunger"] + VISIT_HUNGER)
    treat_count = snacks.count(CAT_TREAT)
    cat["hunger"] = clamp_indicator(cat["hunger"] - CAT_TREAT_HUNGER * treat_count)
    cat["visits_today"] += 1
    cat["history"].append(f"Visit of {minutes} min")
    return cat


def feed_cat(cat):
    """BR08: feeding reduces hunger by 35."""
    cat["hunger"] = clamp_indicator(cat["hunger"] - FEED_HUNGER)
    cat["history"].append("Fed")
    return cat


def nap_cat(cat):
    """BR08: a nap restores 40 energy."""
    cat["energy"] = clamp_indicator(cat["energy"] + NAP_ENERGY)
    cat["history"].append("Nap")
    return cat


def check_alerts(cat):
    """BR09: returns the list of the cat's welfare alerts (may be empty)."""
    alerts = []
    if cat["hunger"] >= HUNGER_ALERT:
        alerts.append(f"{cat['name']} is very hungry!")
    if cat["happiness"] <= HAPPINESS_ALERT:
        alerts.append(f"{cat['name']} is sad!")
    if cat["energy"] <= ENERGY_ALERT:
        alerts.append(f"{cat['name']} is exhausted and needs a nap!")
    return alerts


def register_visit(customer, cat, minutes, snacks):
    """Calculates every value of the visit and returns the sale dictionary.

    Must be called BEFORE apply_visit_effect: it stores the cat's status
    as the customer found it (used for the discount and the receipt).
    """
    status_before = classify_cat_status(cat["energy"])
    time_value = calculate_time_value(minutes)
    rate = calculate_visit_discount_rate(minutes, status_before)
    discount = calculate_discount(time_value, rate)
    snacks_value = calculate_snacks_value(snacks)
    total = calculate_visit_total(time_value, discount, snacks_value)
    return {
        "customer": customer,
        "cat": cat["name"],
        "cat_status": status_before,
        "minutes": minutes,
        "snacks": list(snacks),
        "time_subtotal": time_value,
        "discount_rate": rate,
        "discount": discount,
        "snacks_subtotal": snacks_value,
        "total": total,
    }


def find_most_visited_cats(visits):
    """Returns the list of cats with the most visits (all tied ones). [] if empty."""
    visit_count = {}
    for visit in visits:
        visit_count[visit["cat"]] = visit_count.get(visit["cat"], 0) + 1
    if not visit_count:
        return []
    highest_count = max(visit_count.values())
    most_visited = []
    for name, count in visit_count.items():
        if count == highest_count:
            most_visited.append(name)
    return most_visited


def generate_report(visits):
    """Summarizes the sales of the day: revenue, visits, average ticket, top cats."""
    number_of_visits = len(visits)
    total_revenue = round(sum(visit["total"] for visit in visits), 2)
    snacks_revenue = round(sum(visit["snacks_subtotal"] for visit in visits), 2)
    total_discounts = round(sum(visit["discount"] for visit in visits), 2)
    if number_of_visits > 0:
        average_ticket = round(total_revenue / number_of_visits, 2)  # calculation
    else:
        average_ticket = 0.0
    return {
        "number_of_visits": number_of_visits,
        "total_revenue": total_revenue,
        "snacks_revenue": snacks_revenue,
        "total_discounts": total_discounts,
        "average_ticket": average_ticket,
        "most_visited_cats": find_most_visited_cats(visits),
    }


def build_bar(value, size=10):
    """ASCII bar for a 0-100 indicator: 70 -> '[#######---]'."""
    filled = (value * size + INDICATOR_MAX // 2) // INDICATOR_MAX  # half rounds up
    return "[" + "#" * filled + "-" * (size - filled) + "]"


def create_initial_cats():
    """Pre-registered cats (each one in a different state, for the demonstration)."""
    mochi = create_cat("Mochi", "Sleepy")
    sushi = create_cat("Sushi", "Playful")
    sushi["energy"] = 35                        # starts Tired
    boba = create_cat("Boba", "Foodie")
    boba["hunger"] = 75
    boba["energy"] = 60
    nori = create_cat("Nori", "Shy")
    nori["energy"] = 10                         # starts Resting
    nori["happiness"] = 45
    dango = create_cat("Dango", "Playful")
    dango["energy"] = 95
    return [mochi, sushi, boba, nori, dango]


# ==========================================================
# OUTPUT FUNCTIONS (only print)
# ==========================================================

def show_menu():
    print()
    print("===== Neko Cafe (=^.^=) =====")
    print("1. Register a visit")
    print("2. See the cafe cats")
    print("3. Feed a cat")
    print("4. Nap time for a cat")
    print("5. Register a new cat")
    print("6. Daily report")
    print("7. Run automatic tests")
    print("0. Close the cafe")


def show_cat(cat):
    status = classify_cat_status(cat["energy"])
    print(f"\n{cat['name']} {KAOMOJIS[status]}  ({cat['personality']})")
    print(f"  Hunger:    {build_bar(cat['hunger'])} {cat['hunger']:3d}")
    print(f"  Happiness: {build_bar(cat['happiness'])} {cat['happiness']:3d}")
    print(f"  Energy:    {build_bar(cat['energy'])} {cat['energy']:3d}")
    print(f"  Status: {status} | Visits today: {cat['visits_today']}")


def show_cats(cats):
    print("\n----- Neko Cafe kittens -----")
    for cat in cats:
        show_cat(cat)


def show_alerts(alerts):
    for alert in alerts:
        print(f"  [!] ALERT: {alert}")


def show_receipt(visit, cat):
    status_before = visit["cat_status"]                    # as the customer found the cat
    status_after = classify_cat_status(cat["energy"])
    discount_text = describe_discount(status_before, visit["discount_rate"])
    print("\n--- Neko Cafe Receipt ---")
    print(f"Customer: {visit['customer']} | Cat: {visit['cat']} {KAOMOJIS[status_before]}")
    width = 6                                              # aligns the receipt values
    print(f"Time:      {visit['minutes']:>3} min x {format_currency(PRICE_PER_MINUTE)}"
          f" = {format_currency(visit['time_subtotal'], width)}")
    print(f"{discount_text}:".ljust(27)
          + f"- {format_currency(visit['discount'], width)}")
    for snack in visit["snacks"]:
        print(f"  + {snack}".ljust(29) + format_currency(MENU[snack], width))
    print("Snacks:".ljust(29) + format_currency(visit["snacks_subtotal"], width))
    print("VISIT TOTAL:".ljust(29) + format_currency(visit["total"], width))
    print(f"\n{visit['cat']} after the visit: {status_after} {KAOMOJIS[status_after]}")


def show_report(report):
    print("\n===== Daily report (=^.^=)/ =====")
    if report["number_of_visits"] == 0:
        print("No visits registered today. (=;.;=)")
        return
    print(f"Visits registered:     {report['number_of_visits']}")
    print(f"Total revenue:         {format_currency(report['total_revenue'])}")
    print(f"  - from snacks:       {format_currency(report['snacks_revenue'])}")
    print(f"  - discounts given:   {format_currency(report['total_discounts'])}")
    print(f"Average ticket:        {format_currency(report['average_ticket'])}")
    most_visited = report["most_visited_cats"]
    label = "Most visited cat:" if len(most_visited) == 1 else "Most visited cats:"
    print(f"{label:<23}{', '.join(most_visited)}")


def show_visits(visits):
    print("\nVisits of the day:")
    for number, visit in enumerate(visits, start=1):
        print(f"  {number}. {visit['customer']} + {visit['cat']}"
              f" | {visit['minutes']} min | {format_currency(visit['total'])}")


# ==========================================================
# MENU / INPUT FUNCTIONS (only ask for data)
# ==========================================================

def read_text(message):
    """Asks for a non-empty text."""
    while True:
        text = input(message).strip()                      # input()
        if text:
            return text
        print("  Please type something. (=o.o=)")


def read_int(message, minimum, maximum):
    """Asks for an integer between minimum and maximum, repeating until valid."""
    while True:
        number = convert_to_int(input(message))            # input() + int()
        if number is not None and minimum <= number <= maximum:
            return number
        print(f"  Invalid value. Type a number from {minimum} to {maximum}.")


def choose_cat(cats):
    """Shows the numbered cats and returns the chosen one (or None to cancel)."""
    print("\nChoose a kitten:")
    for number, cat in enumerate(cats, start=1):
        status = classify_cat_status(cat["energy"])
        print(f"  {number}. {cat['name']} {KAOMOJIS[status]} - {status}")
    print("  0. Cancel")
    option = read_int("Cat number: ", 0, len(cats))
    if option == 0:
        return None
    return cats[option - 1]


def choose_snacks():
    """Builds the list of snacks ordered (may repeat; 0 finishes)."""
    snack_names = list(MENU)
    snacks = []
    print("\nMenu:")
    for number, name in enumerate(snack_names, start=1):
        print(f"  {number}. {name:<20} {format_currency(MENU[name])}")
    print("  0. Finish order")
    while True:
        option = read_int("Snack (0 to finish): ", 0, len(snack_names))
        if option == 0:
            return snacks
        snacks.append(snack_names[option - 1])
        print(f"  + {snack_names[option - 1]} added!")


def read_minutes(max_allowed):
    """BR10: asks for the visit minutes without crashing on text or wrong range."""
    while True:
        text = input(f"Visit minutes ({MIN_MINUTES} to {max_allowed}): ")  # input()
        minutes = convert_to_int(text)                     # conversion to int
        if validate_minutes(minutes, max_allowed):
            return minutes
        print(f"  Invalid minutes. Use a whole number from {MIN_MINUTES} to {max_allowed}.")


def menu_register_visit(cats, visits):
    cat = choose_cat(cats)
    if cat is None:
        return
    status = classify_cat_status(cat["energy"])
    max_allowed = calculate_allowed_minutes(status)
    if max_allowed == 0:
        print(f"\n{cat['name']} {KAOMOJIS[status]} is resting and cannot receive visits now.")
        print("How about a nap (option 4) or choosing another kitten?")
        return
    if status == STATUS_TIRED:
        print(f"\n{cat['name']} is tired: visit of at most {max_allowed} min.")
    customer = read_text("Customer name: ")                # input()
    minutes = read_minutes(max_allowed)
    snacks = choose_snacks()
    visit = register_visit(customer, cat, minutes, snacks)
    visits.append(visit)
    apply_visit_effect(cat, minutes, snacks)
    show_receipt(visit, cat)
    show_alerts(check_alerts(cat))


def menu_feed(cats):
    cat = choose_cat(cats)
    if cat is None:
        return
    feed_cat(cat)
    print(f"\nNom nom! {cat['name']} ate. Hunger now: {cat['hunger']} (=^w^=)")
    show_alerts(check_alerts(cat))


def menu_nap(cats):
    cat = choose_cat(cats)
    if cat is None:
        return
    nap_cat(cat)
    status = classify_cat_status(cat["energy"])
    print(f"\n{cat['name']} took a nap (=u.u=) zZ  Energy: {cat['energy']} -> {status}")
    show_alerts(check_alerts(cat))


def menu_register_cat(cats):
    name = read_text("New kitten's name: ")                # input()
    if find_cat(cats, name) is not None:
        print(f"  There is already a cat named {name}! (=o.o=)")
        return
    print("Personalities:")
    for number, personality in enumerate(PERSONALITIES, start=1):
        print(f"  {number}. {personality}")
    option = read_int("Personality: ", 1, len(PERSONALITIES))
    cat = create_cat(name, PERSONALITIES[option - 1])
    cats.append(cat)
    print(f"\nWelcome, {cat['name']}! (=^.^=)/")


def menu_report(cats, visits):
    report = generate_report(visits)
    show_report(report)
    if visits:
        show_visits(visits)
    print("\nCats' welfare:")
    alerts_of_the_day = []
    for cat in cats:
        alerts_of_the_day.extend(check_alerts(cat))
    if alerts_of_the_day:
        show_alerts(alerts_of_the_day)
    else:
        print("  All kittens are fine! (=^.^=)")


# ==========================================================
# TEST MODE (tests the business functions on their own)
# ==========================================================

def check(description, actual, expected):
    """Compares actual x expected, prints the line and returns True/False."""
    passed = actual == expected
    mark = "OK  " if passed else "FAILED"
    print(f"  [{mark}] {description}: expected={expected!r} actual={actual!r}")
    return passed


def run_tests():
    """Runs the test cases (including boundary values) and shows the score."""
    print("\n===== Automatic tests (=^.^=)7 =====")
    results = []

    print("BR04 - package discount rate:")
    for minutes, expected in [(29, 0.0), (30, 0.10), (59, 0.10), (60, 0.15), (5, 0.0), (120, 0.15)]:
        results.append(check(f"{minutes} min", calculate_discount_rate(minutes), expected))

    print("BR05 - cat status from energy:")
    for energy, expected in [(41, STATUS_AVAILABLE), (40, STATUS_TIRED),
                             (16, STATUS_TIRED), (15, STATUS_RESTING), (0, STATUS_RESTING)]:
        results.append(check(f"energy {energy}", classify_cat_status(energy), expected))

    print("BR05/BR10 - allowed minutes per status:")
    for status, expected in [(STATUS_AVAILABLE, 120), (STATUS_TIRED, 15), (STATUS_RESTING, 0)]:
        results.append(check(status, calculate_allowed_minutes(status), expected))

    print("BR04/BR11 - visit discount (package or tired-cat courtesy):")
    for minutes, status, expected in [(15, STATUS_TIRED, 0.10), (5, STATUS_TIRED, 0.10),
                                      (15, STATUS_AVAILABLE, 0.0), (30, STATUS_AVAILABLE, 0.10),
                                      (60, STATUS_AVAILABLE, 0.15)]:
        results.append(check(f"{minutes} min, {status}",
                             calculate_visit_discount_rate(minutes, status), expected))
    tired_cat = create_cat("Test", "Shy")
    tired_cat["energy"] = 35
    visit = register_visit("Test", tired_cat, 15, [])
    results.append(check("15-min visit with a tired cat (7,50 - 0,75)", visit["total"], 6.75))
    results.append(check("stored status is the one before the visit", visit["cat_status"], STATUS_TIRED))

    print("BR02/BR03 - visit value calculation:")
    results.append(check("time 45 min", calculate_time_value(45), 22.5))
    results.append(check("10% discount on 22,50", calculate_discount(22.5, 0.10), 2.25))
    results.append(check("15% discount on 30,50 (61 min)", calculate_discount(30.5, 0.15), 4.58))
    results.append(check("15% discount on 31,50 (63 min)", calculate_discount(31.5, 0.15), 4.73))
    results.append(check("0% discount on 14,50", calculate_discount(14.5, 0.0), 0.0))
    results.append(check("snacks matcha+taiyaki",
                         calculate_snacks_value(["Matcha latte", "Taiyaki"]), 23.5))
    results.append(check("no snacks", calculate_snacks_value([]), 0.0))
    results.append(check("total 22,50-2,25+23,50", calculate_visit_total(22.5, 2.25, 23.5), 43.75))
    visit = register_visit("Test", create_cat("Test", "Shy"), 60, [CAT_TREAT])
    results.append(check("60-min visit + cat treat", visit["total"], 31.5))
    visit = register_visit("Test", create_cat("Test", "Shy"), 20, [])
    results.append(check("20-min visit without snacks", visit["total"], 10.0))

    print("Registering and finding cats:")
    cat = create_cat("Pudding", "Foodie")
    results.append(check("new cat (hunger, happiness, energy)",
                         (cat["hunger"], cat["happiness"], cat["energy"]), (30, 70, 80)))
    results.append(check("new cat with no visits and empty history",
                         (cat["visits_today"], cat["history"]), (0, [])))
    initial_cats = create_initial_cats()
    results.append(check("initial cats", [initial_cat["name"] for initial_cat in initial_cats],
                         ["Mochi", "Sushi", "Boba", "Nori", "Dango"]))
    results.append(check("initial statuses",
                         [classify_cat_status(initial_cat["energy"]) for initial_cat in initial_cats],
                         [STATUS_AVAILABLE, STATUS_TIRED, STATUS_AVAILABLE,
                          STATUS_RESTING, STATUS_AVAILABLE]))
    for name, expected in [("Mochi", "Mochi"), ("mochi", "Mochi"), ("  NORI ", "Nori"), ("Pudding", None)]:
        found = find_cat(initial_cats, name)
        found_name = found["name"] if found is not None else None
        results.append(check(f"find '{name}'", found_name, expected))

    print("BR01 - indicator limits:")
    for value, expected in [(-10, 0), (50, 50), (130, 100)]:
        results.append(check(f"clamp {value}", clamp_indicator(value), expected))

    print("BR06/BR07 - effect of the visit on the cat:")
    cat = create_cat("Test", "Shy")            # hunger 30, happiness 70, energy 80
    apply_visit_effect(cat, 45, [CAT_TREAT])
    results.append(check("happiness after the visit", cat["happiness"], 85))
    results.append(check("energy after 45 min", cat["energy"], 65))
    results.append(check("hunger after visit + cat treat", cat["hunger"], 15))
    results.append(check("visits_today", cat["visits_today"], 1))

    print("BR08 - staff actions:")
    cat = create_cat("Test", "Foodie")
    cat["hunger"] = 20
    results.append(check("feed with hunger 20", feed_cat(cat)["hunger"], 0))
    cat["energy"] = 80
    results.append(check("nap with energy 80", nap_cat(cat)["energy"], 100))

    print("BR09 - welfare alerts:")
    cat = create_cat("Test", "Shy")
    results.append(check("healthy cat", len(check_alerts(cat)), 0))
    cat["hunger"], cat["happiness"], cat["energy"] = 80, 20, 15
    results.append(check("hunger 80/happiness 20/energy 15", len(check_alerts(cat)), 3))
    cat["hunger"], cat["happiness"], cat["energy"] = 79, 21, 16
    results.append(check("hunger 79/happiness 21/energy 16", len(check_alerts(cat)), 0))

    print("BR10 - minutes validation:")
    for text, maximum, expected in [("4", 120, False), ("5", 120, True), ("120", 120, True),
                                    ("121", 120, False), ("abc", 120, False), ("16", 15, False)]:
        minutes = convert_to_int(text)
        results.append(check(f"'{text}' (max {maximum})", validate_minutes(minutes, maximum), expected))

    print("Formatting and report:")
    results.append(check("format 43.75", format_currency(43.75), "R$ 43,75"))
    results.append(check("format 1234.5", format_currency(1234.5), "R$ 1.234,50"))
    sample_visits = [
        {"cat": "Mochi", "total": 43.75, "snacks_subtotal": 23.5, "discount": 2.25},
        {"cat": "Dango", "total": 31.5, "snacks_subtotal": 6.0, "discount": 4.5},
        {"cat": "Mochi", "total": 10.0, "snacks_subtotal": 0.0, "discount": 0.0},
    ]
    report = generate_report(sample_visits)
    results.append(check("revenue", report["total_revenue"], 85.25))
    results.append(check("average ticket", report["average_ticket"], 28.42))
    results.append(check("most visited cat", report["most_visited_cats"], ["Mochi"]))
    results.append(check("tie Mochi x Dango", find_most_visited_cats(sample_visits[:2]),
                         ["Mochi", "Dango"]))
    results.append(check("empty report", generate_report([])["average_ticket"], 0.0))
    results.append(check("empty report without top cat", generate_report([])["most_visited_cats"], []))

    passed_count = sum(results)
    print(f"\nResult: {passed_count}/{len(results)} tests passed.",
          "(=^.^=)b" if passed_count == len(results) else "(=;.;=)")
    return passed_count, len(results)


# ==========================================================
# MAIN PROGRAM
# ==========================================================

def main():
    cats = create_initial_cats()        # list of dictionaries (cats)
    visits = []                         # list of dictionaries (sales of the day)
    print("Welcome to Neko Cafe! The kittens are waiting. (=^.^=)")
    while True:
        show_menu()
        option = input("Choose an option: ").strip()       # input()
        if option == "1":
            menu_register_visit(cats, visits)
        elif option == "2":
            show_cats(cats)
        elif option == "3":
            menu_feed(cats)
        elif option == "4":
            menu_nap(cats)
        elif option == "5":
            menu_register_cat(cats)
        elif option == "6":
            menu_report(cats, visits)
        elif option == "7":
            run_tests()
        elif option == "0":
            menu_report(cats, visits)
            print("\nCafe closed. See you tomorrow! (=^.^=)/~")
            break
        else:
            print("Invalid option. Choose a number from the menu. (=o.o=)")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nCafe closed in a hurry. See you soon! (=^.^=)/~")
