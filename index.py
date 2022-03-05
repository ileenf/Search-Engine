from collections import defaultdict, Counter
from pydoc import doc
from Posting import Posting
from tokenizer import parse_text, tokenize
import os
import json

DEBUG = True
def debug_print(s):
    if DEBUG:
        print(s)

def calc_field_weighted_tf(orig_tf, field):
    ''' given a tf for a token, return the adjusted term frequency (corresponds to the field in which the token occurred)'''
    field_weights = {"headers": 2,
                    "meta_content": 1.75,
                    "emphasis": 1.5,
                    "paragraph": 1}

    return orig_tf * field_weights[field]

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

def build_doc_to_tokens_index(base_dir: str, weight_adjusted=False)->dict:
    ''' secondary index to assist with doc_length / cosine calculation
        <docID: <token: tf>>'''
    cur_docID = 0
    doc_to_tokens = dict()

    for domain in os.scandir(base_dir):             # each subdir = web domain
        if domain.is_dir():
            for page in os.scandir(domain.path):    # each file within subdir = webpage
                if page.is_file():
                    with open(page.path) as file:
                        cur_docID += 1
                        json_data = json.loads(file.read())
                        content = json_data['content']
                        field_tf_map = parse_text(content)                              
                        tf_map = defaultdict()
                        debug_print(f"{cur_docID}: {page.path}")

                        # for each token, collect the total term frequency across all of the fields it occurs in 
                        for field, cur_field_tfs in field_tf_map.items():
                            for token, freq in cur_field_tfs.items():
                                if weight_adjusted:
                                    # for each field, add the token's field-adjusted term frequency to the token's current total term frequency
                                    tf_map[token] += calc_field_weighted_tf(freq, field)      
                                else:
                                    # each token's term frequency is unaltered
                                    tf_map[token] += freq   

                        doc_to_tokens[cur_docID] = tf_map
                        tf_map.clear()               
    return doc_to_tokens

def build_index(base_dir: str)->dict:
    ''' primary inverted index
        <token: posting list>, where posting list is sorted in decreasing tf
    '''
    cur_docID = 0
    inverted_index = defaultdict(list)

    for domain in os.scandir(base_dir):             # each subdir = web domain
        if domain.is_dir():
            for page in os.scandir(domain.path):    # each file within subdir = webpage
                if page.is_file():
                    with open(page.path) as file:
                        cur_docID += 1
                        # debug_print(f"{cur_docID}: {page.path}")

                        if cur_docID > 20:
                            return inverted_index

                        json_data = json.loads(file.read())
                        content = json_data['content']
                        parsed_content, weighted_tags = parse_text(content)                # bsoup to parse html into a string of tokens
                        tf_map = Counter(tokenize(parsed_content))
                        total_tokens = sum(tf_map.values())
                        for token in tf_map:          # inverted index
                            weighted_count = 0
                            if weighted_tags['headers'] and token in weighted_tags['headers']:
                                weighted_count += (weighted_tags['headers'][token] * HEADER_WT)
                            if weighted_tags['meta_content'] and token in weighted_tags['meta_content']:
                                weighted_count += (weighted_tags['meta_content'][token] * META_CONTENT_WT)
                            if weighted_tags['emphasis'] and token in weighted_tags['emphasis']:
                                weighted_count += (weighted_tags['emphasis'][token] * EMPHASIS_WT)
                            if weighted_tags['paragraph'] and token in weighted_tags['paragraph']:
                                weighted_count += (weighted_tags['paragraph'][token] * P_WT)
                            inverted_index[token].append(Posting(cur_docID, weighted_count, total_tokens))
    return inverted_index


def write_index_to_file(inverted_index: dict, filename='fixed_index.txt'):
    file = open(filename, 'w')
    posting_string = ''
    for token in sorted(inverted_index):                                                                  # sort tokens alphabetically
        posting_string += f'{token}|{len(inverted_index[token])}| '                                       # token, termdocfreq:
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

def write_mapping_to_file(file_name, data_struct):
    ''' write data from a relatively small in-memory data structure to a file
        used for id_url_map and lexicons (seek indexes)
    '''
    with open(file_name, 'w') as index_file:
        for term, value in data_struct.items():
            index_file.write(f'{term}|{value}\n')