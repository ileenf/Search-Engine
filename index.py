from collections import defaultdict, Counter
from Posting import Posting
from tokenizer import parse_text, tokenize, tokenize_two_grams
import os
import json
import psutil
import sys

DEBUG = True
def debug_print(s):
    if DEBUG:
        print(s)

FIELD_WEIGHTS = {"headers": 2,
                "meta_content": 1.75,
                "emphasis": 1.5,
                "paragraph": 1}

def get_all_tokens_from_field_tf_map(field_tf_map) -> set():
    ''' wtmap = <field: <token: unweighted tf>>    one of the two maps returned from parsed_content '''
    all_tkns = set()
    for tf_map in field_tf_map.values():
        all_tkns.update(tf_map.keys())
    return all_tkns

def calc_weighted_tf_by_doc(field_tf_map, weight_adjusted=False) -> dict():
    ''' for each token, get its weight'''
    tf_map = defaultdict(int)
    for field, field_to_tfs_counter in field_tf_map.items():
        for token, freq in field_to_tfs_counter.items():
            if weight_adjusted:                                           # for each field, add the token's field-adjusted term frequency to the token's current total term frequency
                tf_map[token] += freq * FIELD_WEIGHTS[field]       
            else:                                                           # each token's term frequency is unaltered
                tf_map[token] += freq   
    return tf_map

def calc_weighted_tf_by_token(tkn, field_tf_map):
    ''' for each doc, get its weight'''
    weighted_count = 0
    for field in FIELD_WEIGHTS:
        if field in field_tf_map and tkn in field_tf_map[field]:
            orig_weight = field_tf_map[field][tkn]
            weighted_count +=  orig_weight * FIELD_WEIGHTS[field]
    return weighted_count

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

<<<<<<< HEAD
def build_pindexes(base_dir: str, batch_sz=100, mem_threshold=57, idx_size_threshold=1310824):
    cur_batchsz = batch_sz
    cur_docID = 0
    idx_docfirst = 1
    
    inverted_index = defaultdict(list)
=======
def build_index(base_dir: str, weight_adjusted=False)->dict:
    ''' simultaneously constructs inverted_index, doc_to_tokens, two_grams '''
    cur_docID = 0
    inverted_index = defaultdict(list)              # <token: posting list>, where posting list is sorted in decreasing tf
    doc_to_tokens = dict()                          # <docID: <token: token frequency>>
    two_grams = defaultdict(list)                   # <token: posting list>, where token is a 2 gram (spaces removed)
    doc_to_two_grams = dict()
>>>>>>> c06363cd257cfeb842d51bb11996aaaeacd73ded

    for domain in os.scandir(base_dir):             # each subdir = web domain
        if domain.is_dir():
            if not inverted_index:
                inverted_index = defaultdict(list)

            for page in os.scandir(domain.path):    # each file within subdir = webpage
                if page.is_file():
                    with open(page.path) as file:
                        if not inverted_index:
                            inverted_index = defaultdict(list)
                        cur_docID += 1
<<<<<<< HEAD
                        cur_batchsz -= 1
                        debug_print(f'{cur_docID}: {page.path}')
                        json_data = json.loads(file.read())
                        content = json_data['content']
                        parsed_content = parse_text(content)                                # bsoup to parse html into a string of tokens

                        token_mapping = Counter(tokenize(parsed_content))
                        total_tokens = sum(token_mapping.values())
                        for token, count in token_mapping.items(): 
                            inverted_index[token].append(Posting(cur_docID, count, total_tokens))
                
                # after parsing page, check if done with batch
                if cur_batchsz <= 0:
                    cur_batchsz = batch_sz
                    idx_sz = sys.getsizeof(inverted_index) 
                    debug_print(f'RAM % MEMORY USED: {psutil.virtual_memory()[2]}')
                    debug_print(f"Size of inverted_index: {idx_sz}")

                    # dump partial index to file
                    if idx_sz > idx_size_threshold:                                                 
                        write_pindex(inverted_index, doc_first=idx_docfirst, doc_last=cur_docID)
                        inverted_index = None
                        idx_docfirst = cur_docID + 1 # reset docfirst

    # dump one last time
    write_pindex(inverted_index, doc_first=idx_docfirst, doc_last=cur_docID)


def write_pindex(inverted_index: dict, doc_first: int, doc_last: int):
    ''' helper function to be called in build_pindexes'''
    file = open(f'../rsrc/index{doc_first}-{doc_last}.txt', 'w')
    posting_string = ''
    for token in sorted(inverted_index):                                # sort by keys
        posting_string += f'{token}|{len(inverted_index[token])}|'      # token, termdocfreq:
        for posting in inverted_index[token]:
=======
                        debug_print(f'{cur_docID}: {page.path}')

                        json_data = json.loads(file.read())
                        content = json_data['content']
                        field_tf_map, two_grams_field_tf_map = parse_text(content)  

                        all_tokens = get_all_tokens_from_field_tf_map(field_tf_map)

                        debug_print(f'  doc to tokens')
                        tf_map = calc_weighted_tf_by_doc(field_tf_map)  
                        doc_to_tokens[cur_docID] = tf_map

                        debug_print(f'  doc to two grams')
                        # two grams needs a doc to two grams
                        tf_map = calc_weighted_tf_by_doc(two_grams_field_tf_map) 
                        doc_to_two_grams[cur_docID] = tf_map

                        debug_print(f'  inv')
                        for token in all_tokens:         
                            weighted_count = calc_weighted_tf_by_token(token, field_tf_map)
                            inverted_index[token].append(Posting(cur_docID, weighted_count))

                        debug_print(f'  two grams')
                        # two grams need to be weighted too
                        all_two_grams = get_all_tokens_from_field_tf_map(two_grams_field_tf_map)
                        for token in all_two_grams:
                            weighted_count = calc_weighted_tf_by_token(token, two_grams_field_tf_map)
                            two_grams[token].append(Posting(cur_docID, weighted_count))

    return inverted_index, doc_to_tokens, two_grams, doc_to_two_grams

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
>>>>>>> c06363cd257cfeb842d51bb11996aaaeacd73ded
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