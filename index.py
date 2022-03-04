from collections import defaultdict, Counter
from pydoc import doc
from Posting import Posting
from tokenizer import parse_text, tokenize
import os
import json

#directory = './DEV'
# DEBUG = True
# def debug_print(s):
#     if DEBUG:
#         print(s)
headers_weight = 2
meta_content_weight = 1.75
emphasis_weight = 1.5
paragraph_weight = 1

def build_id_url_map(base_dir: str)->dict:
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

def build_index(base_dir: str)->dict:
    cur_docID = 0
    inverted_index = defaultdict(list)
    # doc_to_tokens = dict()

    for domain in os.scandir(base_dir):             # each subdir = web domain
        if domain.is_dir():
            for page in os.scandir(domain.path):    # each file within subdir = webpage
                if page.is_file():
                    with open(page.path) as file:
                        cur_docID += 1
                        # debug_print(f"{cur_docID}: {page.path}")
                        json_data = json.loads(file.read())
                        content = json_data['content']
                        parsed_content, weighted_tags = parse_text(content)                # bsoup to parse html into a string of tokens
                        token_mapping = Counter(tokenize(parsed_content))
                        total_tokens = sum(token_mapping.values())
                        for token, count in token_mapping.items():          # inverted index
                            weighted_count = 0
                            if weighted_tags['headers'] and token in weighted_tags['headers']:
                                weighted_count += (weighted_tags['headers'][token] * headers_weight)
                            if weighted_tags['meta_content'] and token in weighted_tags['meta_content']:
                                weighted_count += (weighted_tags['meta_content'][token] * meta_content_weight)
                            if weighted_tags['emphasis'] and token in weighted_tags['emphasis']:
                                weighted_count += (weighted_tags['emphasis'][token] * emphasis_weight)
                            if weighted_tags['paragraph'] and token in weighted_tags['paragraph']:
                                weighted_count += (weighted_tags['paragraph'][token] * paragraph_weight)
                            inverted_index[token].append(Posting(cur_docID, weighted_count, total_tokens))
                        # doc_to_tokens[cur_docID] = token_mapping            # doc_id: token mapping
    return inverted_index
    # return doc_to_tokens

def write_index_to_file(inverted_index: dict):
    file = open('fixed_index.txt', 'w')
    posting_string = ''
    for token in sorted(inverted_index):                                                                  # sort tokens alphabetically
        posting_string += f'{token}|{len(inverted_index[token])}| '                                       # token, termdocfreq:
        for posting in sorted(inverted_index[token], key=(lambda p: -p.__token_count)):                   # sort posting list by descending tf
            posting_json = json.dumps(posting.__dict__)
            posting_string += posting_json + '|'
        posting_string = posting_string.strip('|')
        file.write(posting_string + '\n')
        posting_string = ''
    file.close()

def index_of_index(index):
    index_file = open(index)
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