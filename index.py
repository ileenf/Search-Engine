from collections import defaultdict, Counter
from Posting import Posting
import os
import json

inverted_index = defaultdict(list)
directory = './DEV'

for domain in os.scandir(directory):  # each subdir = web domain
    if domain.is_dir():
        for page in os.scandir(domain.path):  # each file within subdir = webpage
            if page.is_file():
                with open(page.path) as file:
                    json_data = json.loads(file.read())
                    content = json_data['content']
                    parsed_content =  # bsoup to parse html into a string of tokens
                    token_mapping = Counter(parsed_content)

                    for token, count in token_mapping.items():
                        inverted_index[token].append(Posting(json_data['url'], count, sum(token_mapping.values())))

def write_index_to_file(inverted_index):
    file = open('index.txt', 'w')
    for token, postings in inverted_index.items():
        file.write(token + ": ")
        for posting in postings:
            posting_json = json.dumps(posting.__dict__)
            file.write(posting_json)
        file.write('\n')

    file.close()