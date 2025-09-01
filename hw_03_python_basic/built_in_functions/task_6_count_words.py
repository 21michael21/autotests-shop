def count_words(text):
    return len(text.strip().split())

print(count_words("  Hello, world! This is Python.  "))  # 5
