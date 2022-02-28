from collections import defaultdict, Counter
from Posting import Posting
from tokenizer import parse_text, tokenize
import os
import json
import psutil
import sys

#directory = './DEV'
DEBUG = True

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

def build_index(base_dir: str, batch_sz=100, mem_threshold=57, idx_size_threshold=1310824):
    # retrieve batch of corpus (100 docs?)
    # create posting list
    # if mem < 50%, retrieve another batch 
    # else, dump
    # clear dict

    cur_batchsz = batch_sz
    cur_docID = 0
    idx_docfirst = 1
    
    inverted_index = defaultdict(list)
    for domain in os.scandir(base_dir):             # each subdir = web domain
        if domain.is_dir():
            for page in os.scandir(domain.path):    # each file within subdir = webpage
                if page.is_file():
                    if DEBUG:
                        print(cur_docID)

                    with open(page.path) as file:
                        cur_docID += 1
                        cur_batchsz -= 1
                        print(cur_docID)
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
                    mem = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2         # index 2 = the percent field
                    print(f'RAM % MEMORY USED: {psutil.virtual_memory()[2]}')


                    # other way to do it: check the size of the dasta structure. 
                    idx_sz = sys.getsizeof(inverted_index) 
                    print(f"Size of inverted_index: {idx_sz}")

                    if idx_sz > idx_size_threshold:                                                 # past threshold, so dump
                        write_pindex(inverted_index, doc_first=idx_docfirst, doc_last=cur_docID)
                        inverted_index.clear()
                        printf("after clearing, size of inv_index = {idx_sz}")
                        idx_docfirst = cur_docID + 1 # reset docfirst


def write_pindex(inverted_index: dict, doc_first: int, doc_last: int):
    file = open(f'../rsrc/index{doc_first}-{doc_last}.txt', 'w')
    posting_string = ''
    for token in sorted(inverted_index):                                 # sort by keys
        posting_string += f'{token}|{len(inverted_index[token])}|'     # token, termdocfreq:
        for posting in inverted_index[token]:
            posting_json = json.dumps(posting.__dict__)
            posting_string += posting_json + '|'
        posting_string = posting_string.strip('|')
        file.write(posting_string + '\n')
        posting_string = ''
    file.close()

def write_id_url_map(id_url_map:dict):
    with open('id_url_map.txt', 'w') as file:
        for id, url in id_url_map.items():
            file.write(f'{id}:{url}\n')


def merge_pindexes(num_pindexes, path):
    pass
