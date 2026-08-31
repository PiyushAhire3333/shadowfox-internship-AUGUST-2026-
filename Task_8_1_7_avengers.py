class Avenger:
    LEADER = "Captain America"

    def __init__(self, name, age, gender, super_power, weapon):
        self.name, self.age, self.gender = name, age, gender
        self.super_power, self.weapon = super_power, weapon

    # ── Point 6: Individual Getter Methods ──────────────────────────────────
    get_name        = lambda self: self.name
    get_age         = lambda self: self.age
    get_gender      = lambda self: self.gender
    get_super_power = lambda self: self.super_power
    get_weapon      = lambda self: self.weapon

    def get_info(self):
        return (f"  {'─'*44}\n"
                f"    Name       : {self.get_name()}\n"
                f"     Age        : {self.get_age()}\n"
                f"     Gender     : {self.get_gender()}\n"
                f"     Super Power: {self.get_super_power()}\n"
                f"     Weapon     : {self.get_weapon()}\n"
                f"     Is Leader  : {self.is_leader()}")

    # ── Point 7: is_leader Method ───────────────────────────────────────────
    def is_leader(self):
        return "** Yes — Leader of the Avengers!" if self.name == Avenger.LEADER else "X No"


# ── Points 4 & 5: Hero data (name, age, gender, super_power, weapon) ────────
heroes_data = [
    ("Captain America", 105, "Male",   "Super Strength",    "Shield"),
    ("Iron Man",         48, "Male",   "Technology",        "Armor"),
    ("Black Widow",      36, "Female", "Superhuman",        "Batons"),
    ("Hulk",             49, "Male",   "Unlimited Strength","No Weapon"),
    ("Thor",           1500, "Male",   "Super Energy",      "Mjölnir"),
    ("Hawkeye",          47, "Male",   "Fighting Skills",   "Bow and Arrows"),
]

avengers = [Avenger(*d) for d in heroes_data]

# ── Full Info via get_info() ─────────────────────────────────────────────────
print(f"\n{' AVENGERS TEAM ROSTER ':^48}")
for hero in avengers:
    print(hero.get_info())
print(f"  {'─'*44}")

# ── Individual Getter Demo ───────────────────────────────────────────────────
print(f"\n{' INDIVIDUAL GETTER DEMO':^48}")
print(f"  {'─'*44}")
print(f"  {'Name':<18} {'Power':<22} {'Weapon'}")
print(f"  {'─'*44}")
for h in avengers:
    print(f"  {h.get_name():<18} {h.get_super_power():<22} {h.get_weapon()}")

# ── is_leader() Demo ─────────────────────────────────────────────────────────
print(f"\n{' LEADER CHECK':^48}")
print(f"  {'─'*44}")
for h in avengers:
    print(f"  {h.get_name():<18} → {h.is_leader()}")
print(f"  {'─'*44}\n")