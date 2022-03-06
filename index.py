from collections import defaultdict, Counter
from Posting import Posting
from tokenizer import parse_text, tokenize, tokenize_two_grams
import os
import json

DEBUG = True
def debug_print(s):
    if DEBUG:
        print(s)

FIELD_WEIGHTS = {"headers": 2,
                "meta_content": 1.75,
                "emphasis": 1.5,
                "paragraph": 1}

def calc_field_weighted_tf(orig_tf, field):
    ''' given a tf for a token, return the adjusted term frequency (corresponds to the field in which the token occurred)'''
    return orig_tf * FIELD_WEIGHTS[field]

def build_id_url_map(base_dir: str)->dict:
    ''' auxiliary bookkeeping structure: <docID: url>'''
    cur_docID = 0
    id_url_map = dict()
    for domain in os.scandir(base_dir):  # each subdir = web domain
        if domain.is_dir():
            for page in os.scandir(domain.path):  # each file within subdir = webpage
                if page.is_file():
                    with open(page.path) as file:
                        cur_docID += 1
                        json_data = json.loads(file.read())
                        id_url_map[cur_docID] = json_data['url'] 
    return id_url_map

def build_index(base_dir: str, weight_adjusted=False)->dict:
    ''' simultaneously constructs inverted_index, doc_to_tokens, two_grams '''
    cur_docID = 0
    inverted_index = defaultdict(list)              # <token: posting list>, where posting list is sorted in decreasing tf
    doc_to_tokens = dict()                          # <docID: <token: token frequency>>
    two_grams_index = defaultdict(list)                   # <token: posting list>, where token is a 2 gram (spaces removed)

    for domain in os.scandir(base_dir):             # each subdir = web domain
        if domain.is_dir():
            for page in os.scandir(domain.path):    # each file within subdir = webpage
                if page.is_file():
                    with open(page.path) as file:
                        cur_docID += 1

                        debug_print(f'{cur_docID}: {page.path}')
                        json_data = json.loads(file.read())
                        content = json_data['content']
                        field_tf_map, two_grams = parse_text(content)  

                        all_tokens = set()                                  # set of all tokens in current doc
                        for tf_map in field_tf_map.values():
                            all_tokens.update(tf_map.keys()) 

                        for token in all_tokens:         
                            weighted_count = 0
                            for field in FIELD_WEIGHTS:
                                if field_tf_map[field] and token in field_tf_map[field]:
                                    weighted_count += calc_field_weighted_tf(field_tf_map[field][token], field)
                            inverted_index[token].append(Posting(cur_docID, weighted_count))

                        tf_map = defaultdict(int)
                        for field, field_to_tfs_counter in field_tf_map.items():
                            for token, freq in field_to_tfs_counter.items():
                                if weight_adjusted:                                             # for each field, add the token's field-adjusted term frequency to the token's current total term frequency
                                    tf_map[token] += calc_field_weighted_tf(freq, field)      
                                else:                                                           # each token's term frequency is unaltered
                                    tf_map[token] += freq   
                        doc_to_tokens[cur_docID] = tf_map

                        two_gram_counts = Counter(two_grams)
                        for two_gram, count in two_gram_counts.items():         # 2gram index
                            two_grams_index[two_gram].append(Posting(cur_docID, count))

    return inverted_index, doc_to_tokens, two_grams

def write_doc_to_tokens_file(doc_to_tokens, filename='doc_to_tokens.txt'):
    with open(filename, 'w') as f:
        for docID, tf_map in doc_to_tokens.items():
            f.write(f'{docID}|')
            f.write(json.dumps(tf_map))
            f.write('\n')

# use for 'fixed_index.txt' and '2_gram_index'
def write_index_to_file(inverted_index: dict, index_file):
    file = open(index_file, 'w')
    posting_string = ''
    for token in sorted(inverted_index):                                                                  # sort tokens alphabetically
        posting_string += f'{token}|{len(inverted_index[token])}| '                                       
        for posting in sorted(inverted_index[token], key=(lambda p: (-p._token_count, p._docId))):        # sort posting list by descending tf
            posting_json = json.dumps(posting.__dict__)
            posting_string += posting_json + '|'
        posting_string = posting_string.strip('|')
        file.write(posting_string + '\n')
        posting_string = ''
    file.close()

def index_of_index(index_path):
    ''' construct an in-memory data structure from a lexicon file'''
    index_file = open(index_path)
    token_to_position = dict()

    curr_position = 0
    line = index_file.readline().strip()
    while line != '':
        token = line.split('|', 1)[0]
        token_to_position[token] = curr_position
        curr_position = index_file.tell()
        line = index_file.readline().strip()

    index_file.close()
    return token_to_position

# use for id_url_map, and two seek indexes
def write_mapping_to_file(file, index):
    with open(file, 'w') as index_file:
        for term, value in index.items():
            index_file.write(f'{term}|{value}\n')