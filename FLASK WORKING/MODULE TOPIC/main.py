import math_utils

price = float(input("Enter price: "))
quantity = float(input("Enter quantity: "))
total = math_utils.calculate_total(price, quantity)

print(f"Total Bill: {total}")