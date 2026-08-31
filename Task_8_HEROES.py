class Avenger:
    def __init__(self, name, hero_name, power, weapon):
        self.name       = name        

        self.hero_name  = hero_name   

        self.power      = power      

        self.weapon     = weapon      

    def introduce(self):
        return f"I am {self.hero_name} ({self.name}) | Power: {self.power} | Weapon: {self.weapon}"


iron_man    = Avenger("Tony Stark",       "Iron Man",        "Genius & Tech",           "Iron Suit")
captain     = Avenger("Steve Rogers",     "Captain America", "Super Soldier Serum",      "Vibranium Shield")
thor        = Avenger("Thor Odinson",     "Thor",            "God of Thunder",           "Mjolnir")
hulk        = Avenger("Bruce Banner",     "Hulk",            "Gamma Radiation Strength", "Fists")
black_widow = Avenger("Natasha Romanoff", "Black Widow",     "Master Spy & Combat",      "Widow's Bite")
hawkeye     = Avenger("Clint Barton",     "Hawkeye",         "Perfect Marksmanship",     "Bow & Arrows")


for hero in [iron_man, captain, thor, hulk, black_widow, hawkeye]:
    print(hero.introduce())