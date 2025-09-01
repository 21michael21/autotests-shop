def greet(**kwargs):
    for key, value in kwargs.items():
        print(f"{key} : {value}")

    
greet(name= "John", age= 30, city= "New York")


def greet_standart(**kwargs):
   if 'name' in kwargs:
      print(f"Hello, {kwargs['name']}!")
   else:
      print("Hello!")


greet_standart(name= "John", age= 30, city= "New York")