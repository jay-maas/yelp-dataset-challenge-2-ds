import collections
from awstools.awstools import s3
import pandas as pd
import spacy
from spacy.tokens import Doc
import time


import logging

###Logging###
logger = logging.getLogger(__name__+" NLP Processing")


# using the spacy library to vectorize existing tokens
# these download models
# python -m spacy download en_vectors_web_lg
# python -m spacy download en_core_web_lg
# python -m spacy validate

""" The Functions for NLP"""
# Tokenizing function
# loading the spacy model
nlp = spacy.load("en_core_web_lg")
# Wrap filter/tokenizer
def filter_data(func):
    def wrapper(text):
        return filter_doc(func(text))
    return wrapper

# Filter on stop_words
def filter_doc(doc):
    filtered_sentence = []
    for word in doc:
        lexeme = doc.vocab[word.text]
        if lexeme.is_stop == False:
            if word.is_punct == False:
                filtered_sentence.append(word.text)
    # return filtered_sentence  #  Use to return a list of strings
#     return ' '.join(filtered_sentence)  # Use to return a single string with stop words, punctuation removed
    return Doc(nlp.vocab, filtered_sentence,[True]*len(filtered_sentence))  # Use to return a spacy.tokens.Doc


# Helper functions

# upgraded versions (TODO errors with finding spacy model in parallel process IPython)
@filter_data
def tokenize(x):

    return nlp(x)

# Counting ngram function
def count_ngrams(lines, min_length=2, max_length=4):
    """Iterate through given lines iterator (file object or list of
    lines) and return n-gram frequencies. The return value is a dict
    mapping the length of the n-gram to a collections.Counter
    object of n-gram tuple and number of times that n-gram occurred.
    Returned dict includes n-grams of length min_length to max_length.
    """
    lengths = range(min_length, max_length + 1)
    ngrams = {length: collections.Counter() for length in lengths}
    queue = collections.deque(maxlen=max_length)

    # Helper function to add n-grams at start of current queue to dict
    def add_queue():
        current = tuple(queue)
        for length in lengths:
            if len(current) >= length:
                ngrams[length][current[:length]] += 1

    # Loop through all lines and words and add n-grams to dict
    for line in lines:
        for word in tokenize(line):
            queue.append(word)
            if len(queue) >= max_length:
                add_queue()

    # Make sure we get the n-grams at the tail end of the queue
    while len(queue) > min_length:
        queue.popleft()
        add_queue()
        return ngrams

def token_to_text(x):
  return [token.text for token in x]

def create_nlp_vectors(x):
  return list(x.vector)

def create_noun_chunks(x):
  span_list = []
  for span in list(nlp(' '.join(x)).noun_chunks):
    span_list.append(span.text)
  return span_list

def create_lemmas(doc):
    return [token.lemma_ for token in x]

# The Masta
def run_all(df):
    start_main = time.time()
    # Main loop
    start_token = time.time()
    df['token'] = df['text'].apply(tokenize)
    stop_token = time.time()
    logger.info('Tokenized in {}'.format(stop_token - start_token))

    start_vector = time.time()
    df['token_vector'] = df['token'].apply(create_nlp_vectors)
    stop_vector = time.time()
    logger.info('Vectorized in {}'.format(stop_vector - start_vector))

    start_lemma = time.time()
    df['lemma'] = df['token'].apply(create_lemmas)
    stop_lemma = time.time()
    logger.info('Lemmatized in {}'.format(stop_lemma - start_lemma))

    start_tokentext = time.time()
    df['token'] = df['token'].apply(token_to_text)
    stop_tokentext = time.time()
    logger.info('Coverted to text in {}'.format(stop_tokentext - start_tokentext))

    start_ngram = time.time()
    df['ngram'] = df['token'].apply(create_noun_chunks)
    stop_ngram = time.time()
    logger.info('Noun Chunks in {}'.format(stop_ngram - start_ngram))

    # Time logging
    stop_main = time.time()
    logger.info('Batch of {} processed in {}'.format(len(df), stop_main-start_main))
    return df

"""The master function above will run everything"""