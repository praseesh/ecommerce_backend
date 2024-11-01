import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()

def tokenize(sentence):
    return nltk.word_tokenize(sentence, language='english')

def stem(word):
    return stemmer.stem(word.lower())

def bag_of_words(tokenize_sentence, all_words):
    pass


word = ['organize', 'organizing', 'organizes', 'organizes' ]
stemmed_words = [stem(w) for w in word]
# print(stemmed_words)

# a = "How aren't long does shipping take?"
# print(a)
# tokens = tokenize(a)
# print(tokens)