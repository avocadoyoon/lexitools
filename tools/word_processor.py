# Word Processing Script: Counts repeated words and outputs a clean list + table

# Ask user how they want to input text
choice = input("Type '1' to paste text or '2' to use a file:\n")

# OPTION 1: paste text
if choice == "1":
    text = input("Paste your text here:\n")

# OPTION 2: read from file (you type filename)
elif choice == "2":
    file_name = input("Enter file name (e.g., words.txt):\n")

    with open(file_name, "r", encoding="utf-8") as file:
        text = file.read()

else:
    print("Invalid choice!")
    exit()

# convert everything to lowercase (avoids duplicates)
text = text.lower()

import string  # for punctuation

# remove punctuation BEFORE splitting
text = text.translate(str.maketrans('', '', string.punctuation))

# split text into words (based on spaces)
words = text.split()

# create an empty dictionary to count words
word_counts = {}

# loop through words and count them
for word in words:
    if word in word_counts:
        word_counts[word] += 1
    else:
        word_counts[word] = 1

# find repeated words
repeated_words = []

for word, count in word_counts.items():
    if count > 1:
        repeated_words.append(word)

# get cleaned list (unique words)
unique_words = list(word_counts.keys())

# print results
print("\nRepeated words:")
print(repeated_words)

print("\nCleaned list:")
print(unique_words)

# =========================
# CREATE A TABLE OUTPUT
# =========================

print("\nWord Frequency Table:")
print("----------------------")

# header
print(f"{'Word':<15} {'Count':<10}")

# rows
for word, count in word_counts.items():
    print(f"{word:<15} {count:<10}")
