from tokenizer import tokenize
import json
from collections import defaultdict, Counter
from ranking import tf_rank_top_k, tfidf_rank_top_k
import time

def search(query_words, k, tokens_to_postings, index_of_tokens_to_postings):
    query_words_set = set(query_words)

    doc_freq_map = dict()
    token_freq_map = dict()
    seen_postings = defaultdict(int)

    for word in query_words_set:
        if word not in index_of_tokens_to_postings:
            continue
        seek_position = index_of_tokens_to_postings[word]
        tokens_to_postings.seek(seek_position)
        line = tokens_to_postings.readline()
        line = line.split('|', 2)
        token = line[0]
        freq = line[1]
        posting_strs = line[2]

        doc_freq_map[token] = int(freq)
        for posting in posting_strs.split('|'):
            posting = json.loads(posting)
            posting_id = posting['_docId']
            token_freq_map[posting_id] = posting['_token_count']
            seen_postings[posting_id] += 1

    intersection = []
    for posting_id, count in seen_postings.items():
        if count == len(query_words):
            intersection.append(posting_id)

    if len(query_words_set) == 1:
        # token_freq_map: doc_id mapped to token count
        return intersection, True, token_freq_map

    curr_freq = len(query_words_set)
    while len(intersection) < k and curr_freq > 0:
        # can use seen_postings, since doc id is mapped to the number of tokens
        for doc_id, freq in seen_postings.items():
            if freq == curr_freq:
                intersection.append(doc_id)
        curr_freq -= 1
    # doc_freq_map: each query word mapped to num of documents
    return intersection, False, doc_freq_map

def get_doc_id_to_url_map():
    doc_id_to_url = dict()
    with open('id_url_map.txt') as file:
        lines = file.readlines()
    for line in lines:
        line = line.split(':', 1)
        doc_id = line[0]
        url = line[1]
        doc_id_to_url[doc_id] = url
    return doc_id_to_url


def get_index_of_index(file):
    doc_id_to_position = dict()
    with open(file) as file:
        for line in file:
            line = line.split('|')
            doc_id_to_position[line[0]] = int(line[1])

    return doc_id_to_position

def display_urls(posting_intersection, doc_id_to_url):
    for doc_id in posting_intersection:
        url = doc_id_to_url[str(doc_id)]
        print(url.strip())


if __name__ == '__main__':
    k = 10
    doc_id_to_position = get_index_of_index('index_of_doc_to_tf.txt')
    index_of_tokens_to_postings = get_index_of_index('index_of_main_index.txt')
    tokens_to_postings = open('fixed_index.txt')

    query = input('Enter search: ')
    while query != '':
        
        start_time = time.time()
        query_words = tokenize(query)

        posting_intersection, is_one_word, freq_map = search(query_words, 10, tokens_to_postings, index_of_tokens_to_postings)
        print(len(posting_intersection))
        doc_id_to_url = get_doc_id_to_url_map()
        if is_one_word:
            top_k_doc_ids = tf_rank_top_k(posting_intersection, freq_map, k)
        else:
            top_k_doc_ids = tfidf_rank_top_k(Counter(query_words), k, freq_map, posting_intersection, doc_id_to_position)
        display_urls(top_k_doc_ids, doc_id_to_url)
        print("--- %s milliseconds ---" % ((time.time() - start_time)*1000))

        query = input('Enter search: ')

    tokens_to_postings.close()
