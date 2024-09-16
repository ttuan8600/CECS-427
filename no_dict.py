while True:
    file_name = input("Enter file name: ")
    try:
        days = []
        most = 0
        with open(file_name) as file:
            for line in file:
                if line.startswith("From "):
                    words = line.split()
                    days.append(words[2])
            for i in range (len(days)):
                count = 1
                for j in range(i+1, len(days)):
                    if days[i] == days[j]:
                        count += 1
                if count > most:
                    most = count
                    word = days[i]
            print(word, most)
        break
    except FileNotFoundError:
        print("File not found. Please try again.")