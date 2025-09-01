def pop_until_zero(nums):
    result = []
    while nums and nums[-1] != 0:
        result.append(nums.pop())
    return result

print(pop_until_zero([5, 3, 1, 0, 7, 8]))  # [8, 7]
