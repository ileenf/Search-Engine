from collections import defaultdict, Counter
from pydoc import doc
from Posting import Posting
from tokenizer import parse_text, tokenize
import os
import json

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

def build_index(base_dir: str)->dict:
    cur_docID = 0
    inverted_index = defaultdict(list)
    doc_to_tokens = dict()

    for domain in os.scandir(base_dir):             # each subdir = web domain
        if domain.is_dir():
            for page in os.scandir(domain.path):    # each file within subdir = webpage
                if page.is_file():
                    with open(page.path) as file:
                        cur_docID += 1

                        debug_print(f"{cur_docID}: {page.path}")
                        if cur_docID == 300:
                            return doc_to_tokens

                        json_data = json.loads(file.read())
                        content = json_data['content']
                        parsed_content = parse_text(content)                # bsoup to parse html into a string of tokens
                        token_mapping = Counter(tokenize(parsed_content))
                        # total_tokens = sum(token_mapping.values())
                        # for token, count in token_mapping.items():          # inverted index
                        #     inverted_index[token].append(Posting(cur_docID, count, total_tokens))
                        doc_to_tokens[cur_docID] = token_mapping            # doc_id: token mapping    
    # return inverted_index
    return doc_to_tokens

def write_index_to_file(inverted_index: dict):
    file = open(f'index.txt', 'w')
    posting_string = ''
    for token in sorted(inverted_index):                                # sort by keys
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

def write_doc_to_tokens_map(doc_to_tokens:dict):
    with open('doc_to_tf.txt', 'w') as file:
        for docID in doc_to_tokens:
            file.write(f'{docID}:')
            tkn_str = ''
            for token, token_freq in doc_to_tokens[docID].items():
                tkn_str += json.dumps((token, token_freq)) + '|'
            # remove the last |
            tkn_str = tkn_str[:-1]     
            file.write(tkn_str + '\n')
