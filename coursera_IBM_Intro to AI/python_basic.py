"""#List and Tuples#"""

"""#List"""
from symtable import Class


my_list = [10, 20, 30, 40, 50] 
my_list.insert(2, 6) # Insert number 6 at index 2
#expected output: [10, 20, 6, 30, 40, 50]
removed_element = my_list.pop(2) # Removes and returns the element at index 2 
print(my_list)
#expected output: [10, 20, 30, 40, 50]

my_list = [1, 2, 3, 4, 5] 
print(my_list[1:4]) 
# Output: [2, 3, 4] (elements from index 1 to 3)
print(my_list[:3]) 
# Output: [1, 2, 3] (elements from the beginning up to index 2) 
print(my_list[2:]) 
# Output: [3, 4, 5] (elements from index 2 to the end) 
print(my_list[::2]) 
# Output: [1, 3, 5] (every second element)

"""#Tuples"""
my_tuple = (1, 2, 3, 4, 5)
print(my_tuple[1])  # Output: 2
"""Tuples has len, min, max, sum functions"""

"""Disctionary"""
d = {'a': 1, 'b': 2, 'c': 3} #Key: Value pairs

"""set"""
"""sets are unordered collections of unique elements"""
my_set = {1, 2, 3, 4, 5}
my_set2 = {4, 5, 6, 7, 8}
union_set = my_set.union(my_set2)  # {1, 2, 3, 4, 5, 6, 7, 8}
intersection_set = my_set.intersection(my_set2)  # {4, 5}
difference_set = my_set.difference(my_set2)  # {1, 2, 3}
my_set.add(6)  # Adds 6 to the set
my_set.remove(3)  # Removes 3 from the set


""" Function """
def Mult(a, b):
    c = a * b
    return(c)
result = Mult(12,2)
print(result) # Expected output: 24


