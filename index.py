from collections import defaultdict, Counter
from Posting import Posting
from tokenizer import parse_text, tokenize
import os
import json

#directory = './DEV'

DEBUG = True

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
                        
                        if DEBUG:
                            print(json_data['url'] + '---')
                        token_mapping = Counter(tokenize(parsed_content))
                        total_tokens = sum(token_mapping.values())

                        

                        for token, count in token_mapping.items():
                            
                            p = Posting(cur_docID, count, total_tokens)
                            inverted_index[token].append(p)

                        if DEBUG:
                            print(f"<docID={p.get_docID()}, url={json_data['url']}>")

                        
    if DEBUG:
        print("================Finished building index.=============")

    return inverted_index

def write_index_to_file(inverted_index):
    if DEBUG:
        print("================Writing index.=============")

    file = open('index.txt', 'w')
    for token in sorted(inverted_index):            # sort by keys
        if DEBUG:
            print(f"Writing: {token}")

        file.write(token + ": ")
        for posting in inverted_index[token]:
            posting_json = json.dumps(posting.__dict__)
            file.write(posting_json)
        file.write('\n')

    file.close()

    if DEBUG:
        print("================Finished writing index.=============")