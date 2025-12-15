"""Download data from web"""
from pyodide.http import pyfetch
import pandas as pd
filename = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-PY0101EN-SkillsNetwork/labs/Module%204/data/example1.txt"
async def download(url, filename):
    response = await pyfetch(url)
    if response.status == 200:
        with open(filename, "wb") as f:
            f.write(await response.bytes())
await download(filename, "example1.txt")
print("done")


"""Read txt file"""
with open("example1.txt", "r") as file1: #'r' for reading, 'w' for writing, 'a' for appending
    FileContent = file1.read()
    FileContent1 = file1.readline(1) #or can use \n to read line by line
    print(FileContent)

"""Copy txt file"""
with open("example1.txt", "r") as file1:
    with open("example2.txt", "w") as file2:
        for line in file1:
            file2.write(line)

""" Pandas """
import pandas as pd
data = {
    "Name": ["Alice", "Bob", "Charlie", "David"],
    "Age": [24, 27, 22, 32],
    "City": ["New York", "Los Angeles", "Chicago", "Houston"]
}   
df = pd.DataFrame(data)
print(df)
print(df.iloc[2])   # Access the third row by position
print(df.loc[1])    # Access the second row by label
print(df.iloc[2])   # Access the third row by position
high_above_102 = df[df['Age'] > 25]
print(high_above_102)