from bs4 import BeautifulSoup
import urllib3

url = input(">")
html = urllib3.request.urlopen(url)
soup = BeautifulSoup(html)

print(soup)
# # using Dict
# while True:
#     file_name = input("Enter file name: ")
#     try:
#         my_dict = {}
#         with open(file_name) as file:
#             for line in file:
#                 if line.startswith("From "):
#                     words = line.split()
#                     my_dict[words[2]] = my_dict.get(words[2], 0) + 1
#             m = sorted(((v,k) for k, v in my_dict.items()), reverse=True)
#             print(m[0][1], ":", m[0][0])
#         break
#     except FileNotFoundError:
#         print("File not found. Please try again.")

# # brute force
# while True:
#     file_name = input("Enter file name: ")
#     try:
#         days = []
#         most = 0
#         with open(file_name) as file:
#             for line in file:
#                 if line.startswith("From "):
#                     words = line.split()
#                     days.append(words[2])
#                 day = set(days)
#             for i in range(len(days)):
#                 count = 1
#                 for j in range(i + 1, len(days)):
#                     if days[i] == days[j]:
#                         count += 1
#                 if count > most:
#                     most = count
#                     word = days[i]
#             print(word, most)
#         break
#     except FileNotFoundError:
#         print("File not found. Please try again.")
# # brute force 2
# while True:
#     file_name = input("Enter file name: ")
#     try:
#         days = []
#         day = None
#         most = 0
#         with open(file_name) as file:
#             for line in file:
#                 if line.startswith("From "):
#                     words = line.split()
#                     days.append(words[2])
#                 d = set(days)
#             for i in d:
#                 count = days.count(i)
#                 if count > most:
#                     most = count
#                     day = i
#             print(day, most)
#         break
#     except FileNotFoundError:
#         print("File not found. Please try again.")
# lst = [1, 2, [3, 4], [5, [100, 200, ['hello']], 23, 11], 1, 7]
# print(lst[3][1][2][0])

# Exe 2
# while True:
#     file_name = input("Enter file name: ")
#     try:
#         with open(file_name) as file:
#             sum_confidence = 0
#             count = 0
#             for line in file:
#                 if line.startswith("X-DSPAM-Confidence"):
#                     pos = line.find(' ')
#                     value = float(line[pos+1:])
#                     sum_confidence += value
#                     count += 1
#
#             if count > 0:
#                 print("Average spam confidence:", sum_confidence / count)
#             else:
#                 print("No valid 'X-DSPAM-Confidence' lines found.")
#         break  # exit loop after successful processing
#     except FileNotFoundError:
#         print("File not found. Please try again.")
# Exe 5
# str = "X-DSPAM-Confidence:0.8475"
# pos = str.find(':')
# value = float(str[pos+1:])
# print("Answer:",type(value), value)

# def paygrade(hours, rate):
#     if hours > 40: 
#         #calculate total pay when employee work more than 40 hours
#         pay = (40*rate) + ((hours-40)*rate*1.5)
#     else:    
#         # Calculate the total pay
#         pay = hours * rate

#     return pay

# def main():
#     exit = True
#     while exit:
#         try:
#             hours= float(input("Enter the hours: "))
#             rate = float(input ("Enter the rate: "))
#             pay = paygrade(hours, rate)
#             print("Pay:", pay)
#             choice = input("Continue(Y/N)? ")
#             if choice.lower() == "n":
#                 exit = False
#             print()
#         except:
#             print("Invalid input. Please enter a number.")


# main()
