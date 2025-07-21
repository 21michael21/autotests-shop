
class Rectangle:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
    
    def area(self)-> int:
        return self.width * self.height
    
    def __eq__(self, obj):
        return self.area() == obj.area()
    
    def __lt__(self, obj):
        return self.area() < obj.area()
    
    def __le__(self, obj):
        return self.area() <= obj.area()
    
    def __gt__(self, obj):
        return self.area() > obj.area()
    
    def __ge__(self, obj):
        return self.area() >= obj.area()
    
    def __ne__(self, obj):
        return self.area() != obj.area()



rectangle1 = Rectangle(1, 1)
rectangle2 = Rectangle(2, 2)
rectangle3 = Rectangle(2, 2)

print(rectangle1 == rectangle2)  # False
print(rectangle2 == rectangle3)  # True
print(rectangle1 < rectangle2)   # True
print(rectangle2 < rectangle3)   # False
print(rectangle2 <= rectangle3)  # True
