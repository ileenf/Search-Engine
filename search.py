from tokenizer import tokenize, tokenize_two_grams_from_list
import json
from collections import Counter
from ranking import tf_rank_top_k, tfidf_rank_top_k, get_k_largest
import time

def get_url(docID, id_url_map):
    return id_url_map[str(docID)].strip()

def search(query_words, k, tokens_to_postings, index_of_tokens_to_postings, is_one_term, r=50):
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
        
        plist = posting_strs.split('|')
        num_postings_to_grab = min(r, len(plist))

        # grab up to the top r highest tf for each query term
        for posting in plist[0:num_postings_to_grab]:   
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
    with open('auxiliary/id_url_map.txt') as file:
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
    index_of_doc_to_tf = get_index_of_index('lexicons/index_of_doc_to_tf.txt')
    index_of_doc_to_tf_2grams = get_index_of_index('lexicons/index_of_doc_to_tf_2grams.txt')

    index_of_tokens_to_postings = get_index_of_index('lexicons/index_of_inverted_index.txt')
    index_of_two_grams = get_index_of_index('lexicons/index_of_2_gram_index.txt')
    tokens_to_postings = open('indexes/inverted_index.txt')
    two_grams_to_postings = open('indexes/2gram_index.txt')
    doc_id_to_url = get_doc_id_to_url_map()

    query = input('Enter search: ')
    while query != '':
        
        start_time = time.time()
        query_words = tokenize(query)

        if len(query_words) == 1:
            posting_intersection, freq_map = search(query_words, k, tokens_to_postings, index_of_tokens_to_postings, True)
            top_k_doc_ids = tf_rank_top_k(posting_intersection, freq_map, k)
        else:
            two_gram_query_words = tokenize_two_grams_from_list(query_words)
            two_grams_intersection, two_gram_freq_map = search(two_gram_query_words, k, two_grams_to_postings, index_of_two_grams, False)

            one_gram_intersection = []
            one_gram_freq_map = dict()
            if len(two_grams_intersection) < k:
                one_gram_intersection, one_gram_freq_map = search(query_words, k, tokens_to_postings, index_of_tokens_to_postings, False)
                one_gram_intersection = [docID for docID in one_gram_intersection if docID not in two_grams_intersection]

            # pass in both index_of_doc_to_tf
            top_r_2grams = tfidf_rank_top_k(Counter(two_gram_query_words), k, 
                                            two_gram_freq_map,
                                            two_grams_intersection,
                                            index_of_doc_to_tf_2grams, 'auxiliary/doc_to_tf_2grams.txt'
                                            )

            top_r_1grams = tfidf_rank_top_k(Counter(query_words), k, 
                                            one_gram_freq_map,
                                            one_gram_intersection,
                                            index_of_doc_to_tf, 'auxiliary/doc_to_tf.txt'
                                            )
            # merge them 
            top_k_doc_ids = get_k_largest(top_r_2grams + top_r_1grams, k)
            
        display_urls(top_k_doc_ids, doc_id_to_url)
        print("--- %s milliseconds ---" % ((time.time() - start_time)*1000))

        query = input('Enter search: ')
