from collections import defaultdict, Counter
from Posting import Posting
from tokenizer import parse_text, tokenize
import os
import json

#directory = './DEV'

def build_index(base_dir):
    cur_docID = 0

    inverted_index = defaultdict(list)
    for domain in os.scandir(base_dir):  # each subdir = web domain
        if domain.is_dir():
            for page in os.scandir(domain.path):  # each file within subdir = webpage
                if page.is_file():
                    
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

def write_index_to_file(inverted_index):
    file = open('index.txt', 'w')
    for token in sorted(inverted_index):            # sort by keys
        file.write(token + ": ")
        for posting in inverted_index[token]:
            posting_json = json.dumps(posting.__dict__)
            file.write(posting_json)
        file.write('\n')

    file.close()