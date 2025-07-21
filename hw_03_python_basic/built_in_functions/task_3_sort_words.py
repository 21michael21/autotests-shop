def sort_words(words,var:int = 1):
    if var == 1:
        return sorted(words)
    elif var == 2:
        words.sort()
        return words
    else:
        print("Никак")

print(sort_words(["banana", "apple", "cherry"], var = 1))
print(sort_words(["banana", "apple", "cherry"], var = 2))
