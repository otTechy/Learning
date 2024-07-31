#Coursera Python Class 1 - Last week  - final
largest = None
smallest = None
while True:
	num = input('Number: ')
	try:
		num = int(num)
	except:
		if num == 'done':
			break
		else:
			print('Invalid input')
		continue
# need to see smallestfirst, then largest
	if smallest is None or num < smallest:
		smallest = num
	else largest is None or num > largest:
		largest = num
print('Maximum is', largest)
print('Minimum is', smallest)

#Coursera Python Class 2 - week 3 - Assignment 7.1
#way 1
fname = 'words.txt'#input("Enter file name: ")
fh = open(fname) #open just a file handle, not really read the file
fh= fh.read()
fh = fh.strip()
fh = print(fh.upper())
#way 2
fname = 'words.txt'#input("Enter file name: ")
fh = open(fname) #open just a file handle, not really read the file
for lx in fh:
	lx = lx.rstrip()
	print(lx.upper())


#Coursera Python Class 2 - week 3 - Assignment 7.2
fname = 'mbox-short.txt'
fn = open(fname)
count = 0
test = 0
for line in fn:
    if not line.startswith('X-DSPAM-Confidence:'):
        continue
    count = count +1
    i = line.find('0')
    test = test + float(line[i:])
	# or can use below
	# i = line.split()
    # test = test + float(i[1])
print('Average spam confidence:',test/count)


#Coursera Python Class 2 - week 4 - Assignment 8.4
fname = 'romeo.txt'
fh = open(fname)
lst = list()
for line in fh:
    test = line.split()
    for i in test:
        if i not in lst:
            lst.append(i)
        continue
lst.sort()
print(lst)


#Coursera Python Class 2 - week 4 - Assignment 8.5
# List
fname = input('file name:')
if len(fname) < 1:
fname = "mbox-short.txt"
fh = open(fname)
lst = list() 
num = 0
for line in fh:
    if not line.startswith('From '):
        continue
    num = num + 1    
    test = line.split()
    lst.append(test[1])
for i in lst: # this for loop print out each item in the list to a new line
    print(i)
print("There were", num, "lines in the file with From as the first word")


#Coursera Python Class 2 - week 5 - Assignment 9.4
# Dictionary
# find who send the email, show email address and count
name = input("Enter file:")
if len(name) < 1:
    name = "mbox-short.txt"
fh = open(name)
d = dict()
for line in fh:
    if not line.startswith('From '):
        continue
    test = line.split()
    test = test[1]
    if test not in d:
        d[test] = 1
    else:
        d[test] = d[test]+1
    # way1 to print largest
print(max(d,key= d.get),d.get(max(d,key= d.get)))
    # way2 to print largest
largest = 0
word = None
for k,v in d.items():
    if v > largest:
        largest = v
        word = k
print(word, largest)


#Coursera Python Class 2 - week 6 - Assignment 10.2
# Tuple
name = input('Enter file:')
if len(name) <1: 
    name = "mbox-short.txt"
fn = open(name)
d = dict()
lst = list()
for line in fn:
    if not line.startswith('From '):
        continue
    test = line.split()
    test = test[5]
    time = test[:2]
    if time not in d:
        d[time] = 1
    else:
        d[time] = d[time] + 1
x= sorted(d.items()) #this is how to sort dictionary
for k,v in x:
    lst.append([k,v])
    print(k,v)

#Coursera Python Class 3 - week 2 - Assignment 11
# regular expression, Answer:429011
import re
name = input('File Name: ')
if len(name)<1: name = 'regex_sum_1507253.txt'
fn = open(name)
z=0
x=0
for line in fn:
    y=re.findall('[0-9]+',line)
    for z in y:
        z=int(z)
        x=x+z
print(x)
#below is short way to solve the issue, can't figure out
# Python 3:
# import re
# print( sum( [ ****** *** * in **********('[0-9]+',**************************.read()) ] ) )