class ListContextManager:
    def __init__(self,dupl_list:list):
        self.dupl_list = dupl_list

    def __enter__(self):
        self.test_list = self.dupl_list.copy()
        return self.dupl_list
    
    def __exit__(self, type, value, traceback):
        self.dupl_list.clear()
        self.dupl_list.extend(self.test_list)


test_list = [1, 2, 3]

with ListContextManager(test_list) as lst:
    lst.append(4)
    print("Inside context:", lst)  # [1, 2, 3, 4]
print("Outside context:", test_list)  # [1, 2, 3]