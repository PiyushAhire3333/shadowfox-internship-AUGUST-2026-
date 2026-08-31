australia = ["Sydney", "Melbourne", "Brisbane", "Perth"]
uae       = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman"]
india     = ["Mumbai", "Bangalore", "Chennai", "Delhi"]

city = input("Enter a city name: ")

if city in australia:
    print(f"{city} is in Australia")
elif city in uae:
    print(f"{city} is in UAE")
elif city in india:
    print(f"{city} is in India")
else:
    print(f"{city} is not found in the list")


# This code checks if a given city is in one of the three predefined lists of cities for Australia, UAE, and India. It prompts the user to input a city name and then checks which country the city belongs to, printing the result accordingly. If the city is not found in any of the lists, 
# it informs the user that the city is not found.                          