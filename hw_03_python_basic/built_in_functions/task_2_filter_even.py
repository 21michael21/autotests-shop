def filter_even(nums):
 return list(filter(lambda x: x % 2 == 0 , nums))

print(filter_even([1, 2, 3, 4, 5, 6]))  # [2, 4, 6]