from tokenizer import tokenize
import json
from collections import defaultdict

def search(query):
    query_words = tokenize(query)
    tokens_to_postings = open('tester.txt')

    query_words_set = set(query_words)
    seen_postings = defaultdict(int)

    for line in tokens_to_postings:
        if not query_words_set:
            break
        line = line.split('|', 2)
        token = line[0]
        freq = line[1]
        posting_strs = line[2]
        if token in query_words_set:
            query_words_set.remove(token)
            for posting in posting_strs.split('|'):
                posting = json.loads(posting)
                posting_id = posting['_docId']
                seen_postings[posting_id] += 1
    tokens_to_postings.close()

    intersection = []
    for posting_id, count in seen_postings.items():
        if count == len(query_words):
            intersection.append(posting_id)
    return intersection

def get_doc_id_to_url_map():
    doc_id_to_url = dict()
    with open('id_url_map.txt') as file:
        lines = file.readlines()
    for line in lines:
        line = line.split(':', 1)
        doc_id = line[0]
        url = line[1]
        doc_id_to_url[doc_id] = url
    return doc_id_to_url


def display_urls(posting_intersection, doc_id_to_url):
    for doc_id in posting_intersection[:5]:
        url = doc_id_to_url[str(doc_id)]
        print(url.strip())


if __name__ == '__main__':
    query = input('Enter search: ')
    posting_intersection = search(query)
    doc_id_to_url = get_doc_id_to_url_map()
    display_urls(posting_intersection, doc_id_to_url)
