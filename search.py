from tokenizer import tokenize
import json
from collections import defaultdict, Counter
from ranking import tf_rank_top_k, tfidf_rank_top_k
import time

def search(query_words, k):
    tokens_to_postings = open('fixed_index.txt')

    query_words_set = set(query_words)

    doc_freq_map = dict()
    token_freq_map = dict()
    seen_postings = defaultdict(int)

    for line in tokens_to_postings:
        if not query_words_set:
            break
        line = line.split('|', 2)
        token = line[0]
        freq = line[1]
        posting_strs = line[2]
        if token in query_words_set:
            doc_freq_map[token] = int(freq)
            query_words_set.remove(token)
            for posting in posting_strs.split('|'):
                posting = json.loads(posting)
                posting_id = posting['_docId']
                token_freq_map[posting_id] = posting['_token_count']
                seen_postings[posting_id] += 1
    tokens_to_postings.close()

    intersection = []
    for posting_id, count in seen_postings.items():
        if count == len(query_words):
            intersection.append(posting_id)

    if len(query_words_set) == 1:
        # token_freq_map: doc_id mapped to token count
        return intersection, True, token_freq_map

    curr_k = k - 1
    while len(intersection) < k and curr_k > 0:
        # can use seen_postings, since doc id is mapped to the number of tokens
        for doc_id, freq in seen_postings.items():
            if freq == curr_k:
                intersection.append(doc_id)
        curr_k -= 1
    # doc_freq_map: each query word mapped to num of documents
    return intersection, False, doc_freq_map

def get_doc_id_to_url_map(path: str):
    doc_id_to_url = dict()
    with open(path) as file:
        lines = file.readlines()
    for line in lines:
        line = line.split(':', 1)
        doc_id = line[0]
        url = line[1]
        doc_id_to_url[doc_id] = url
    return doc_id_to_url


def display_urls(posting_intersection, doc_id_to_url):
    for doc_id in posting_intersection:
        url = doc_id_to_url[str(doc_id)]
        print('\t'+url.strip())


if __name__ == '__main__':
    k = 10
    while True:
        query = input('Enter search: ')
        start_time = time.time()
        query_words = tokenize(query)

        posting_intersection, is_one_word, freq_map = search(query_words, 10)
        doc_id_to_url = get_doc_id_to_url_map()
        if is_one_word:
            top_k_doc_ids = tf_rank_top_k(posting_intersection, freq_map, k)
        else:
            top_k_doc_ids = tfidf_rank_top_k(Counter(query_words), k, freq_map, posting_intersection)
        display_urls(top_k_doc_ids, doc_id_to_url)
        print("--- %s milliseconds ---" % ((time.time() - start_time)*1000))
