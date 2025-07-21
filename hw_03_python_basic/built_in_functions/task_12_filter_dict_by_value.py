def filter_dict_by_value(d, threshold):
    return dict(filter(lambda item: item[1] > threshold, d.items()))

print(filter_dict_by_value({'x': 10, 'y': 3, 'z': 7}, 5))
# {'x': 10, 'z': 7}
