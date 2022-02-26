import math
import json


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

def get_all_wts(doc_id, index_file):
    ''' calculates tf-wt for every term that appears in the doc corresponding to doc_id
        returns a dict of <token: tf-wt>
    '''
    token_to_wt = dict()
    tokens_to_postings = open(index_file)

    for line in tokens_to_postings:
        line = line.split('|', 2)
        token = line[0]
        freq = line[1]              # don't need this for this fcn
        posting_strs = line[2]

        for posting in posting_strs.split('|'):
            posting = json.loads(posting)

            if posting['_docID'] > doc_id:
                # doc corresponding to doc_id doesn't contain this token
                break
            elif posting['_docID'] == doc_id:
                # calculate tf-wt
                token_to_wt[token] = calc_tf_wt(posting['_token_count'])
                break

    tokens_to_postings.close()
    return token_to_wt

def calc_doc_score(doc_id, intersection, index_file)->"{str: int}":
    ''' (lnc = Logarithm, No idf, Cosine n'lization)
        only calculates n'lized score for terms in query-doc intersection
        returns a dict of <token: n'lized score>
    '''
    token_to_nlize = dict();

    # need to calculate weights for all terms in the doc in order to calc cosine similarity
    wts = get_all_wts(doc_id, index_file)    
    doc_length = calculate_cosine_similarity(wts.values())

    for term in intersection:
        token_to_nlize[term] = wts[term] / doc_length

    return token_to_nlize


# def get_rankings(query):
    # query_doc_intersections = {p1: [best, insurance], p2: [best], p3: [best, car]}
    # query_nlizedscores = calc_query_score()
    # for doc_id, intersection in query_doc_intersections.items():
    #     doc_nlizedscores = calc_doc_score(doc_id, intersection, index_file)
    #     
    #     bugcheck: if len(doc_score) != len(query_score):   cause error, even though this shouldn't happen
    #     final_score = 0
    #     for term in intersection:
    #       final_score += doc_nlizedscores[term] * query_nlizedscores[term]

