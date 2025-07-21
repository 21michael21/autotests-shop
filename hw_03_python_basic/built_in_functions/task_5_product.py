from functools import reduce

def product(nums):
    return reduce(lambda x, y: x * y, nums)

print(product([1, 2, 3, 4]))  # 24
