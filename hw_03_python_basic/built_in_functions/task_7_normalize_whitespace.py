def normalize_whitespace(text):
    return ' '.join(text.split())

print(normalize_whitespace("This   is   a    test"))  # "This is a test
