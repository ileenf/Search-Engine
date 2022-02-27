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

def get_doc_to_tfwt(doc_id, doc_to_tf_file)->'<token: tfwt>':
    ''' retrieve all the tf_wts for a doc'''
    token_freq_dict = dict()
    file = open(doc_to_tf_file)
    for line in file:
        line = line.split(':', 1)
        if line[0] == str(doc_id):
            # do some sort of dbug check here?
            if line[1].strip() == '':
                break
        
            for entry in line[1].split('|'):
                entry = json.loads(entry)
                token_freq_dict[entry[0]] = calc_tf_wt(entry[1])
            break
    file.close()
    return token_freq_dict

# def get_all_wts(doc_id, doc_to_tokens_file):
#     ''' calculates tf-wt for every term that appears in the doc corresponding to doc_id
#         returns a dict of <token: tf-wt>
#     '''
#     token_to_wt = dict()
#     search.get_doc_to_tokens(doc_id)
#     for line in tokens_to_postings:
#         line = line.split('|', 2)
#         token = line[0]
#         freq = line[1]              # don't need this for this fcn
#         posting_strs = line[2]

#         for posting in posting_strs.split('|'):
#             posting = json.loads(posting)

#             if posting['_docID'] > doc_id:
#                 # doc corresponding to doc_id doesn't contain this token
#                 break
#             elif posting['_docID'] == doc_id:
#                 # calculate tf-wt
#                 token_to_wt[token] = calc_tf_wt(posting['_token_count'])
#                 break

#     tokens_to_postings.close()
#     return token_to_wt

def calc_doc_score(intersection, wts)->"<str: int>":
    ''' (lnc = Logarithm, No idf, Cosine n'lization)
        only calculates n'lized score for terms in query-doc intersection
        returns a dict of <token: n'lized score>
    '''
    token_to_nlize = dict();

    # if wts was empty, eg there weren't any terms
    if len(wts) == 0:
        return 0
    
    # need to calculate weights for all terms in the doc in order to calc cosine similarity   
    doc_length = calculate_cosine_similarity(wts.values())

    for term in intersection:
        token_to_nlize[term] = wts[term] / doc_length

    return token_to_nlize



