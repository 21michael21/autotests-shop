def process_numbers(nums):
    return sorted(map(lambda x: x**2, filter(lambda x: x % 2 == 0, nums)), reverse=True)

print(process_numbers([5, 2, 7, 4, 1, 8]))  # [64, 16, 4]