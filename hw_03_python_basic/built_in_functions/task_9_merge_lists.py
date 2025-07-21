def merge_lists(a, b):
    a_copy = a[:]
    a_copy.extend(b)
    return a_copy


def merge_list_alt(a, b):
    return a + b

print(merge_lists([1, 2], [3, 4]))  # [1, 2, 3, 4]
print(merge_list_alt([1, 2], [3, 4]))  # [1, 2, 3, 4]