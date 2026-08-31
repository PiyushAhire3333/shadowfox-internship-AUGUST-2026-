australia = ["Sydney", "Melbourne", "Brisbane", "Perth"]
uae       = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman"]
india     = ["Mumbai", "Bangalore", "Chennai", "Delhi"]

def get_country(city):
    if city in australia:
        return "Australia"
    elif city in uae:
        return "UAE"
    elif city in india:
        return "India"
    else:
        return None

city1 = input("Enter the first city: ")
city2 = input("Enter the second city: ")

country1 = get_country(city1)
country2 = get_country(city2)

if country1 is None or country2 is None:
    print("One or both cities were not found in the list.")
elif country1 == country2:
    print(f"Both cities are in {country1}")
else:
    print("They don't belong to the same country")


# This code defines a function `get_country` that checks which country a given city belongs to based on predefined lists of cities for Australia, UAE, and India. It prompts the user to input two city names and then checks if both cities belong to the same country. If one or both 
# cities are not found in the lists, it informs the user accordingly.         