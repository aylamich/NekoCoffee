# Neko Cafe (=^.^=) — RA1

Project of the course **AI-Assisted Python for Business Problem Solving** (PUCPR, Prof. Evandro Zatti).

A terminal Python script for a **kawaii cat cafe**: it calculates the value of each visit, records the sales of the day and controls which kittens can receive visits according to each cat's welfare.

> (=^･ω･^=)ﾉ♡ **[full documentation on Notion](https://app.notion.com/p/Documentation-Neko-Coffe-3ec7cf6803c7804b94a5fa2dbbc15e62)** — artifacts, prompts and all the kitty secrets inside! ☕🐾

```
--- Neko Cafe Receipt ---
Customer: Ana | Cat: Mochi (=^.^=)
Time:       45 min x R$ 0,50 = R$  22,50
Package discount (10%):    - R$   2,25
  + Matcha latte             R$  14,00
  + Taiyaki                  R$   9,50
Snacks:                      R$  23,50
VISIT TOTAL:                 R$  43,75

Mochi after the visit: Available (=^.^=)
```

---

## 1. How to run

Requirement: Python 3 (standard library only; tested with Python 3.14.3 on Windows 11).

```bash
python neko_coffee.py
```

Menu:

```
===== Neko Cafe (=^.^=) =====
1. Register a visit
2. See the cafe cats
3. Feed a cat
4. Nap time for a cat
5. Register a new cat
6. Daily report
7. Run automatic tests
0. Close the cafe
```

To test the functions without the menu:

```bash
python -c "import neko_coffee; neko_coffee.run_tests()"
```

Files:

| File | Content |
|---|---|
| `neko_coffee.py` | The script |
| `docs/TESTS.md` | Input → Expected → Actual → Passed? tables for every rule and function, plus the end-to-end run |
| `AIPY_ST1 - Course Project.pdf` | Course brief |

The full RA1 documentation (artifacts and the prompts used with the AI) is on Notion — link on the project page.

> Prices are in Brazilian reais and use the Brazilian format (`R$ 43,75`), because the cafe operates in Brazil.

---

## 2. The business problem (Step 1)

**Business context.** Neko Cafe is a cat cafe. Customers pay for the time they spend with the resident kittens (Mochi, Sushi, Boba, Nori and Dango) and can order snacks. The cats are not products: they get tired, hungry and need to rest between visits.

**Problem.** For every visit, the cafe must calculate how much to charge (time, package discount and snacks). Throughout the day, it must record the sales and know which cats can receive visits and which ones need food or rest.

**Purpose.**
- The **attendant** knows right away how much to charge and which cat is available.
- The **owner** sees the daily revenue (total, number of visits, average ticket and most visited cats) and gets alerts when a cat needs care.
- The business result is the **correct value of each sale** plus the **daily revenue**, without overloading the cats.

---

## 3. IPO model (Step 2)

| | Description |
|---|---|
| **INPUT** | Customer name · chosen cat · visit minutes · snacks ordered · staff actions (feed, nap, register a cat with name and personality) · menu option |
| **PROCESSING** | Time value (minutes × R$ 0,50) · discount rate (package or tired-cat courtesy) · discount in reais · snacks total · visit total · cat status from energy (if/elif/else) · minutes allowed per status · effect of the visit on the cat · welfare alerts · report (sum, average, count) |
| **OUTPUT** | Receipt formatted as `R$ 0,00` · cat panel with ASCII bars and kaomojis · alerts · daily report |

---

## 4. Business rules

| # | Rule | Value | Where |
|---|---|---|---|
| BR01 | Cat indicators are integers from 0 to 100, always clamped | `min`/`max` | `clamp_indicator` |
| BR02 | Price per minute of visit | R$ 0,50 | `PRICE_PER_MINUTE`, `calculate_time_value` |
| BR03 | Visit value | minutes × price − discount + snacks | `calculate_visit_total`, `register_visit` |
| BR04 | Package discount, **only on the time value** (if/elif/else) | ≥ 60 min → 15% · ≥ 30 min → 10% · otherwise 0%. Rounded to the cent, half a cent rounds up | `calculate_discount_rate`, `calculate_discount` |
| BR05 | Cat status from energy (if/elif/else), checked **before** the visit | > 40 Available · > 15 Tired (max. 15 min) · otherwise Resting (blocked) | `classify_cat_status`, `calculate_allowed_minutes` |
| BR06 | Effect of a visit | happiness +15 · energy −1 every 3 min · hunger +5 | `apply_visit_effect` |
| BR07 | "Cat treat" ordered in the visit | hunger −20 per treat | `apply_visit_effect` |
| BR08 | Staff actions | Feed: hunger −35 · Nap: energy +40 | `feed_cat`, `nap_cat` |
| BR09 | Welfare alerts | hunger ≥ 80 · happiness ≤ 20 · energy ≤ 15 | `check_alerts` |
| BR10 | Input validation | whole minutes from 5 to 120 (up to 15 for a tired cat); invalid input never crashes the program | `convert_to_int`, `validate_minutes`, `read_int`, `read_minutes` |
| BR11 | Tired-cat courtesy (replaces the package discount) | 10% on the time value | `TIRED_CAT_DISCOUNT`, `calculate_visit_discount_rate` |

Simulation (details in `docs/TESTS.md`, section 3): a rested cat handles about 2 h of visits before becoming "Tired", and a nap gives back about 2 h.

---

## 5. Data structures

| Structure | Type | Role |
|---|---|---|
| `PERSONALITIES` | `list` | Options when registering a cat |
| `MENU` | `dict` | Snack → price (`float`) |
| `KAOMOJIS` | `dict` | Status → ASCII kaomoji |
| cat (`create_cat`) | `dict` | **One** business thing: `name`, `personality` (str) · `hunger`, `happiness`, `energy`, `visits_today` (int) · `history` (list) |
| `cats` | `list` of `dict` | All the cats of the cafe (5 pre-registered) |
| visit (`register_visit`) | `dict` | **One** sale: `customer`, `cat`, `cat_status` (as the customer found the cat), `minutes`, `snacks` (list), `time_subtotal`, `discount_rate`, `discount`, `snacks_subtotal`, `total` |
| `visits` | `list` of `dict` | Sales of the day, base of the report |

---

## 6. Functions (split by role)

**Business**: calculate and use `return`; never use `input()` or `print()`.

| Function | Parameters → return | Purpose |
|---|---|---|
| `clamp_indicator` | value → int | BR01 |
| `format_currency` | value, width → str | `R$ 1.234,50` |
| `calculate_time_value` | minutes → float | BR02 |
| `calculate_discount_rate` | minutes → float | BR04 (if/elif/else) |
| `calculate_visit_discount_rate` | minutes, status → float | BR11 or BR04 |
| `describe_discount` | status, rate → str | Discount text on the receipt |
| `calculate_discount` | time_value, rate → float | BR04 in cents |
| `calculate_snacks_value` | snacks → float | Sum of the menu prices |
| `calculate_visit_total` | time, discount, snacks → float | BR03 |
| `classify_cat_status` | energy → str | BR05 (if/elif/else) |
| `calculate_allowed_minutes` | status → int | BR05/BR10 (if/elif/else) |
| `convert_to_int` | text → int or None | Safe conversion |
| `validate_minutes` | minutes, max_allowed → bool | BR10 |
| `create_cat` / `create_initial_cats` | → dict / list | Registration |
| `find_cat` | cats, name → dict or None | Prevents duplicated names |
| `apply_visit_effect` | cat, minutes, snacks → dict | BR06/BR07 |
| `feed_cat` / `nap_cat` | cat → dict | BR08 |
| `check_alerts` | cat → list | BR09 |
| `register_visit` | customer, cat, minutes, snacks → dict | Builds the sale |
| `find_most_visited_cats` | visits → list | Report (all tied cats) |
| `generate_report` | visits → dict | Revenue, average ticket, etc. |
| `build_bar` | value → str | `[######----]` |

**Output** (only print): `show_menu`, `show_cat`, `show_cats`, `show_alerts`, `show_receipt`, `show_report`, `show_visits`.

**Menu/input** (only ask for data): `read_text`, `read_int`, `read_minutes`, `choose_cat`, `choose_snacks`, `menu_register_visit`, `menu_feed`, `menu_nap`, `menu_register_cat`, `menu_report`, `main`.

**Tests:** `check`, `run_tests` (65 checks, menu option 7).

---

## 7. Where each requirement is met

Line numbers refer to `neko_coffee.py`.

### Brief requirements (PDF)

| ID | Requirement | Where |
|---|---|---|
| R01 | Calculation/processing task in the chosen context (prices, durations, percentages, indicators) | Visit value, discount %, energy/hunger/happiness, revenue |
| R02 | Meaningful business result | Receipt with the sale total + daily report (revenue, average ticket, most visited cats) |
| R03 | Step 1: Business context | Section 2 of this README + docstring (lines 1–29) |
| R04 | Step 1: Problem | Same |
| R05 | Step 1: Purpose, starting from the need and not from the code | Same |
| R06 | Step 2: INPUT / PROCESSING / OUTPUT | Section 3 + docstring (IPO) |
| R07 | Step 2: Business rules | Section 4 + constants (lines 33–86) |
| R08 | Step 3: business information in variables | Constants, `cats`, `visits`, `time_value`, `discount`… |
| R09 | Step 3: appropriate data types | `int` (minutes, indicators), `float` (prices), `str`, `bool`, `list`, `dict` |
| R10 | Step 3: receives information with `input()` | `read_text` (426), `read_int` (435), `read_minutes` (473), `main` (691) |
| R11 | Step 3: at least one meaningful calculation, stored in variables | `register_visit` (259): `time_value`, `rate`, `discount`, `snacks_value`, `total`; `generate_report` (300) |
| R12 | Step 3: clear output with `print()`/f-strings | `show_receipt` (379), `show_report` (397), `show_cat` (359) |
| R13 | Document the AI interaction (prompt, response, accepted, rejected, why) | Notion documentation ("AI Prompt Used" section of each artifact + "06 — AI Interaction Log") |

### Project technical rules

| Rule | Status |
|---|---|
| Python 3, standard library only, one file | ok: no `import` |
| No classes, no persistence, no GUI | ok |
| Identifiers, comments and messages in English, ASCII only (kaomojis included) | ok: the `.py` is 100% ASCII |
| Business functions without `input()`/`print()` | ok |
| Business rule constants in UPPERCASE at the top | ok |
| Comments marking `input()`, conversions and calculations | ok: `# input()`, `# conversion…`, `# calculation` |
| Invalid input never crashes the program | ok: text, range, menu, blocked cat, duplicated name, Ctrl+C/EOF |
| `if __name__ == "__main__": main()` | ok (line 714) |
