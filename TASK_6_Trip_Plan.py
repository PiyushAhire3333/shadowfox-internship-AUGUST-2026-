your_expenses     = {"Hotel": 1200, "Food": 800, "Transportation": 500, "Attractions": 300, "Miscellaneous": 200}
partner_expenses  = {"Hotel": 1000, "Food": 900, "Transportation": 600, "Attractions": 400, "Miscellaneous": 150}

your_total, partner_total = sum(your_expenses.values()), sum(partner_expenses.values())

print(f"Your Total: ${your_total} | Partner's Total: ${partner_total}")
print(f"{'You' if your_total > partner_total else 'Partner'} spent more by ${abs(your_total - partner_total)}")

max_cat = max(your_expenses, key=lambda k: abs(your_expenses[k] - partner_expenses[k]))
print(f"Biggest difference: {max_cat} (${abs(your_expenses[max_cat] - partner_expenses[max_cat])})")


# in the TASK_6_List.py file, the code snippet defines a list of friends' names and 
# calculates the length of each name, storing the results in a list of tuples. 
# It then prints the friends' names along with their corresponding lengths in a formatted manner.