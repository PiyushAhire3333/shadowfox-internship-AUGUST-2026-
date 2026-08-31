friends_names = ["Alice", "Benjamin", "Charlotte", "David", "Evelyn", "Franklin"]
 
print("=" * 55)
print("        TASK 1: Friends' Names & Name Lengths")
print("=" * 55)
print(f"\nFriends List: {friends_names}\n")
 

friends_tuples = [(name, len(name)) for name in friends_names]
 
print("List of Tuples (Name, Length):")
print("-" * 35)
for name, length in friends_tuples:
    print(f"  {name:<12} → Length: {length}")

