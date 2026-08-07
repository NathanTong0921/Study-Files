with open('document.txt', 'r') as file:
    document = file.read()
tokens = document.lower().split()
unique_vocabulary = set(tokens)
word_frequencies = {}
for word in tokens:
    if word in word_frequencies:
        word_frequencies[word] += 1
    else:
        word_frequencies[word] = 1

print("Tokens:", tokens)
print("Vocabulary:", unique_vocabulary)
print("Vocabulary Size:", len(unique_vocabulary))
print("Word Frequencies:", word_frequencies)