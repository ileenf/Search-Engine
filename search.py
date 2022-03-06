from tokenizer import tokenize, tokenize_two_grams
import json
from collections import defaultdict, Counter
from ranking import tf_rank_top_k, tfidf_rank_top_k
import time

def search(query_words, k, tokens_to_postings, index_of_tokens_to_postings, is_one_term):
    query_words_set = set(query_words)

    doc_freq_map = dict()
    token_freq_map = dict()
    doc_to_num_query_terms = defaultdict(int)

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
            doc_to_num_query_terms[posting_id] += 1

    intersection = []
    for posting_id, count in doc_to_num_query_terms.items():
        if count == len(query_words):
            intersection.append(posting_id)

    if is_one_term:
        # token_freq_map: doc_id mapped to token count
        return intersection, token_freq_map

    curr_freq = len(query_words_set)
    while len(intersection) < k and curr_freq > 0:
        # can use doc_to_num_query_terms, since doc id is mapped to the number of tokens
        for doc_id, freq in doc_to_num_query_terms.items():
            if freq == curr_freq:
                intersection.append(doc_id)
        curr_freq -= 1
    # doc_freq_map: each query word mapped to num of documents
    return intersection, doc_freq_map

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
    index_of_two_grams = get_index_of_index('index_of_2_gram_index.txt')
    tokens_to_postings = open('fixed_index.txt')
    two_grams_to_postings = open('2gram_index.txt')
    doc_id_to_url = get_doc_id_to_url_map()

    query = input('Enter search: ')
    while query != '':
        
        start_time = time.time()
        query_words = tokenize(query)

        if len(query_words) == 1:
            posting_intersection, freq_map = search(query_words, k, tokens_to_postings, index_of_tokens_to_postings, True)
            top_k_doc_ids = tf_rank_top_k(posting_intersection, freq_map, k)
        else:
            two_gram_query_words = tokenize_two_grams(query_words)
            two_grams_intersection, freq_map = search(two_gram_query_words, k, two_grams_to_postings, index_of_two_grams, False)
            print('num two grams', len(two_grams_intersection))

            if len(two_grams_intersection) < k:
                posting_intersection, next_freq_map = search(query_words, k, tokens_to_postings, index_of_tokens_to_postings, False)
                print('num one grams', len(posting_intersection))
                two_grams_intersection += posting_intersection
                freq_map.update(next_freq_map)
            top_k_doc_ids = tfidf_rank_top_k(Counter(two_gram_query_words), k, freq_map, two_grams_intersection, doc_id_to_position)

        display_urls(top_k_doc_ids, doc_id_to_url)
        print("--- %s milliseconds ---" % ((time.time() - start_time)*1000))

        query = input('Enter search: ')

    tokens_to_postings.close()
