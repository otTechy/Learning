"""Object Oriented Programming"""
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

    @abstractmethod
    def circumference(self):
        pass

class CircleObject(Shape):
    def __init__(self, radius): # !!! self,radius are paremeter. Arguments is the values passed in when calling. 
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2
    
    def circumference(self):
        return 2 * 3.14 * self.radius

class Circle(object):

    # constructor
    def __init__(self, radius=1, color='black'): #default values 1, 'black'
        self.radius = radius
        self.color = color

    # method
    def add_radius(self, r):
        self.radius = self.radius + r
        return self.radius
    
    # method
    def drawcircle(self):
        plt.gca().add_patch(plt.Circle((0, 0), self.radius, color=self.color))
        plt.axis('scaled')
        plt.show()

RedCircle = Circle(10, 'red')
RedCircle.add_radius(5)
print(f"RedCircle radius: {RedCircle.radius}")
print(f"RedCircle color: {RedCircle.color}")
RedCircle.drawcircle()


"""Text Analysis"""
class TextAnalyzer:
    def __init__(self,text):
        formattedtext = text.replace('.',' ').replace('!', ' ').replace('?',' ').replace(',',' ').lower()        
        self.fmttext = formattedtext

    def freqAll(self):
        wordslist = self.fmttext.split(' ')
        freqMap = {}
        for i in set(wordslist): # use set to remove duplicates in list, "i" can be anything, can be named "word" etc. 
            freqMap[i] = wordslist.count(i)
        return freqMap
        
    def freqOf(self, word):
        freqdict = self.freqAll()
        if word in freqdict:
            return freqdict[word]
        else:
            return 0

analyzed = TextAnalyzer('what do you think about this? do you like it! i like the way we do proj management.')
print(analyzed.fmttext)
# print(analyzed.wordslist) can print out due to In the TextAnalyzer class, wordslist is a local variable inside the freqAll() method, not an instance attribute.
print(analyzed.freqAll())
print(analyzed.freqOf('you'))