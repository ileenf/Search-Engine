from collections import defaultdict, Counter
from Posting import Posting
from tokenizer import parse_text, tokenize
import os
import json

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

def build_index(base_dir: str)->dict:
    cur_docID = 0
    inverted_index = defaultdict(list)
    for domain in os.scandir(base_dir):             # each subdir = web domain
        if domain.is_dir():
            for page in os.scandir(domain.path):    # each file within subdir = webpage
                if page.is_file():
                    if DEBUG:
                        print(cur_docID)

                    with open(page.path) as file:
                        cur_docID += 1
                        json_data = json.loads(file.read())
                        content = json_data['content']
                        parsed_content = parse_text(content) # bsoup to parse html into a string of tokens

                        token_mapping = Counter(tokenize(parsed_content))
                        total_tokens = sum(token_mapping.values())
                        for token, count in token_mapping.items(): 
                            inverted_index[token].append(Posting(cur_docID, count, total_tokens))
    return inverted_index

def write_index_to_file(inverted_index: dict):
    file = open(f'index.txt', 'w')
    posting_string = ''
    for token in sorted(inverted_index):                            # sort by keys
        posting_string += f'{token}|{len(inverted_index[token])}| '     # token, termdocfreq:
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
