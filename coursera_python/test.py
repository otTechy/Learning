print("hello")


# Get all docstring from the function
def square(n):
    '''Takes in a number n, returns the square of n'''
    return n**2
print(square.__doc__)


# Use key value arguments
def greet(**kwargs):
    for key, value in kwargs.items():
        print(f"{key} means {value} in this argument")
        #f string, which output key = value

greet(name="Alice", age=30, city="New York") 
#name, age, city are the keyword (aka: key)