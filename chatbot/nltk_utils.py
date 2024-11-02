import nltk
from nltk.stem.porter import PorterStemmer
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

nltk.download('punkt')
nltk.download('punkt_tab')
stemmer = PorterStemmer()

def tokenize(sentence):
    return nltk.word_tokenize(sentence, language='english')

def stem(word):
    return stemmer.stem(word.lower())

def bag_of_words(tokenize_sentence, all_words):
    tokenize_sentence = [stem(w) for w in tokenize_sentence]
    bag = np.zeros(len(all_words), dtype=np.float32)
    for idx, w in enumerate(all_words):
        if w in tokenize_sentence:
            bag[idx] = 1.0
    return bag
sentence = ["hello", "how", "are", "you"]
words = ["hi", "hello", "I", "you","are", "bye", "thank", "cool"]
bag = bag_of_words(sentence, words)

word = ['organize', 'organizing', 'organizes', 'organizes' ]
stemmed_words = [stem(w) for w in word]


# a = "How aren't long does shipping take?"
# print(a)
# tokens = tokenize(a)
# print(tokens)