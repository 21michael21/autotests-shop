def square_odds(nums):
    return list(map(lambda x: x**2, filter(lambda x: x % 2 != 0, nums)))

print(square_odds([1, 2, 3, 4, 5]))  # [1, 9, 25]