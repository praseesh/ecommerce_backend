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

class ChatDataset(Dataset):
    def __init__(self,x_train,y_train):
        self.n_samples = len(x_train)
        self.x_data = x_train
        self.y_data = y_train
        
    def __getitem__(self, idx):
        return self.x_data[idx], self.y_data[idx]
    
    def __len__(self):
        return self.n_samples
batch_size = 8
dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True, num_workers=2)
word = ['organize', 'organizing', 'organizes', 'organizes' ]
stemmed_words = [stem(w) for w in word]
# print(stemmed_words)

# a = "How aren't long does shipping take?"
# print(a)
# tokens = tokenize(a)
# print(tokens)