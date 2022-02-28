import math
import json
import heapq


def calc_tf_wt(token_count):
    ''' calculates tf-wt '''
    if token_count > 0:
        return 1 + math.log10(token_count)
    else:
        return 0

def calculate_cosine_similarity(weights):
    ''' given an iterable of weights, calculates cosine similarity '''
    count = 0
    for weight in weights:
        count += (weight**2)
    return math.sqrt(count)

def query_ltc_ranking(query_terms: dict, doc_freq_map: dict):
    term_to_score = dict()
    normalized_scores = dict()

    for term, term_freq in query_terms.items():
        term_freq_weight = 1 + math.log10(term_freq)
        inverted_doc_freq = math.log10(55393/doc_freq_map[term])
        score_weight = term_freq_weight * inverted_doc_freq
        term_to_score[term] = score_weight

    cosine_similarity = calculate_cosine_similarity(term_to_score.values())
    for term, score in term_to_score.items():
        normalized = score / cosine_similarity
        normalized_scores[term] = normalized

    return normalized_scores


def get_doc_to_tfwt(doc_id, doc_to_tf_opened_file) -> '<token: tfwt>':
    ''' retrieve all the tf_wts for a doc'''
    token_freq_dict = dict()
    for line in doc_to_tf_opened_file:
        line = line.split(':', 1)
        if line[0] == str(doc_id):
            # do some sort of dbug check here?
            if line[1].strip() == '':
                break

            for entry in line[1].split('|'):
                entry = json.loads(entry)
                token_freq_dict[entry[0]] = calc_tf_wt(entry[1])
            break
    return token_freq_dict

def doc_lnc_ranking(query_words, doc_term_weights)->"{str: int}":
    ''' (lnc = Logarithm, No idf, Cosine n'lization)
        only calculates n'lized score for terms in query-doc intersection
        returns a dict of <token: n'lized score>
    '''
    token_to_nlize = dict();

    # if wts was empty, eg there weren't any terms
    if len(doc_term_weights) == 0:
        return dict()

    # need to calculate weights for all terms in the doc in order to calc cosine similarity
    doc_length = calculate_cosine_similarity(doc_term_weights.values())
    for term in doc_term_weights.keys():
        if term in query_words:
            token_to_nlize[term] = doc_term_weights[term] / doc_length

    return token_to_nlize

def get_k_largest(scores, k):
    heapq.heapify(scores)
    k_largest = heapq.nlargest(k, scores)
    k_largest_doc_ids = [ele[1] for ele in k_largest]

    return k_largest_doc_ids

def tfidf_rank_top_k(query_words_count, k, doc_freq_map, doc_ids):
    query_and_doc_ranking = []

    # gets mapping of query term to score
    query_scores = query_ltc_ranking(query_words_count, doc_freq_map)

    # get weights of
    doc_to_token_freq_file = open('doc_to_tf.txt')

    for doc_id in doc_ids:
        # get weights of token of curr doc
        doc_term_weights = get_doc_to_tfwt(doc_id, doc_to_token_freq_file)
        # gives mapping of tokens in document to score
        doc_scores = doc_lnc_ranking(query_words_count.keys(), doc_term_weights)
        total_score = 0
        for term in doc_scores:
            total_score += (query_scores[term] * doc_scores[term])

        query_and_doc_ranking.append((total_score, doc_id))

    doc_to_token_freq_file.close()

    # heapify mapping and get top k
    k_largest_doc_ids = get_k_largest(query_and_doc_ranking, k)

    return k_largest_doc_ids

def tf_rank_top_k(doc_ids, token_freq_map, k):
    query_scores = []
    for doc_id in doc_ids:
        query_scores.append(((1 + math.log10(token_freq_map[doc_id])), doc_id))

    k_largest_doc_ids = get_k_largest(query_scores, k)
    return k_largest_doc_ids

if __name__ == '__main__':
    tfidf_rank_top_k({'car':1, 'best':1, 'insurance':1}, 1, {'car':10000, 'best':50000, 'insurance':1000, 'auto': 5000}, [1])
