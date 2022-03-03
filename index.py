from collections import defaultdict, Counter
from Posting import Posting
from tokenizer import parse_text, tokenize
import os
import json
import psutil
import sys

#directory = './DEV'
DEBUG = True
def debug_print(s):
    if DEBUG:
        print(s)

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

def build_pindexes(base_dir: str, batch_sz=100, mem_threshold=57, idx_size_threshold=1310824):
    cur_batchsz = batch_sz
    cur_docID = 0
    idx_docfirst = 1
    
    inverted_index = defaultdict(list)

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
