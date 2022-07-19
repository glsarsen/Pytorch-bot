import nltk
import numpy as np
from nltk.stem import PorterStemmer
from nltk.stem import SnowballStemmer

# stemmer = PorterStemmer()
stemmer = SnowballStemmer("russian")
# nltk.download('punkt')
def tokenize(sentence):
    return nltk.word_tokenize(sentence)

def stem(word):
    return stemmer.stem(word.lower())

def bag_of_words(tokenized_sentence, all_words):
    tokenized_sentence = [stem(w) for w in tokenized_sentence]
    bag = np.zeros(len(all_words), dtype=np.float32)
    for idx, w in enumerate(all_words):
        if w in tokenized_sentence:
            bag[idx] = 1.0

    # second_bag = [1 if w in tokenized_sentence else 0 for w in all_words]
    # print(second_bag)
    return bag
