# import required module
import os
import json
import tokenizer
import index
import search
import ranking
from collections import Counter, defaultdict
from Posting import Posting

 
# assign directory
directory = './DEV'
idurlmap_path= 'id_url_map.txt'
index_path = 'index.txt'
doc_to_tf_path = 'doc_to_tf.txt'
pindex_dir = '../rsrc'
 

def compare(f1, f2):
    f1 = open(f1, 'r')
    f2 = open(f2, 'r')
    fail = False
    count = 1
    line1, line2 = f1.readline().strip().split('|'), f2.readline().strip().split('|')

    if line1 != line2:
            # check the tokens
            if line1[:2] !=  line2[:2]:
                fail = True
                print("Tokens not the same on line {count}")
                print(line1[:2])
                print(line2[:2])

            if len(line1)!= len(line2):
                fail = True
                print("Posting list len not the same on line {count}")
                print(len(line2) - len(line1))
            
            for l1, l2 in zip(line1, line2):
                if l1 != l2 and json.loads(l1)['_token_count'] != json.loads(l2)['_token_count']:
                    print(f'                line1 = {l1}, line2 = {l2}')
                    fail = True

    count = 1
    while line1 != '' and line2 != '' and count < 2:
        line1, line2 = f1.readline().strip().split('|'), f2.readline().strip().split('|')
        if line1 != line2:
            # check the tokens
            if line1[:2] !=  line2[:2]:
                fail = True
                print("Tokens not the same on line {count}")
                print(line1[:2])
                print(line2[:2])

            if len(line1)!= len(line2):
                fail = True
                print("Posting list len not the same on line {count}")
                print(len(line2) - len(line1))
            
            for l1, l2 in zip(line1, line2):
                if l1 != l2 and json.loads(l1)['_token_count'] != json.loads(l2)['_token_count']:
                    print(f'                line1 = {l1}, line2 = {l2}')
                    fail = True
        count += 1
    
    if fail:
        print('NO MATCH!')
    else:
        print('SUCCESS!!')

    f1.close()
    f2.close()

if __name__ == "__main__":
    compare('indexes/inverted_index.txt', 'correct files/inverted_index.txt')
    compare('indexes/2gram_index.txt', 'correct files/2gram_index.txt')

        



