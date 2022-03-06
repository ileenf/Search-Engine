# import required module
import os
import json
from bs4 import BeautifulSoup
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
    line1, line2 = f1.readline(), f2.readline()
    if line1 != line2:
            print(f'NO MATCH on line {count}:')
            print(f'line1 = {line1}')
            print(f'line2 = {line2}')

    count = 1
    while line1 != '' and line2 != '' and count < 19:
        line1, line2 = f1.readline(), f2.readline()
        if line1 != line2:
            print(f'NO MATCH on line {count}:')
            print(f'line1 = {line1}')
            print(f'line2 = {line2}')
            fail = True
        count += 1
    
    if fail:
        print('NO MATCH! LINE NO IS DIFFERENT')
    else:
        print('SUCCESS!!')

    f1.close()
    f2.close()

# # fix version
# with open('./DEV/w3_ics_uci_edu/96f7f58a68c25a8a59e6e1cf264b435250298411b5ea7ccab8938993335446ac.json') as file:
#     json_data = json.loads(file.read())
#     content = json_data['content']
#     parsed_content, weighted_tags, two_gram_tokens = tokenizer.parse_text(content)


# print("\nweighted tags =========")
# for x in weighted_tags:
#     print(f'{x}: {weighted_tags[x]}')

# print("\ntwo_gram_tokens =========")
# for x in two_gram_tokens:
#     print(f'{x}: {weighted_tags[x]}')

# # main version
# with open('./DEV/w3_ics_uci_edu/96f7f58a68c25a8a59e6e1cf264b435250298411b5ea7ccab8938993335446ac.json') as file:
#     json_data = json.loads(file.read())
#     content = json_data['content']
#     parsed_content, weighted_tags = tokenizer.parse_text(content)

#     tokens = tokenizer.tokenize(parsed_content)
#     print("====== tokens =======")
#     print(tokens)
#     print()

#     two_gram_tokens = tokenizer.tokenize_two_grams(tokens)

# print("\nweighted tags =========")
# for x in weighted_tags:
#     print(f'{x}: {weighted_tags[x]}')

# print("\ntwo_gram_tokens =========")
# for x in two_gram_tokens:
#     print(f'{x}: {weighted_tags[x]}')




# merge_pindex.merge_pindexes(pindex_dir)

# without li, a changes
# inv, doc, two_inv, two_doc = index.build_index(directory)
# print('writing inv')
# index.write_index_to_file(inv, 'indexes/ntf_order_index.txt')
# print('writing doc_to_tf')
# index.write_doc_to_tokens_file(doc, 'indexes/nunw_doc_to_tf.txt')
# print('writing two')
# index.write_index_to_file(two_inv, 'indexes/ntf_order_2gram_index.txt')
# print('writing doc_to_twogram')
# index.write_doc_to_tokens_file(two_doc, 'indexes/nunw_doc_to_2gram.txt')

seek = index.index_of_index('bookkeeping/doc_to_tf.txt')
index.write_mapping_to_file('lexicons/index_of_doc_to_tf.txt', seek)

seek = index.index_of_index('bookkeeping/doc_to_tf_2grams.txt')
index.write_mapping_to_file('lexicons/index_of_doc_to_tf_2grams.txt', seek)

seek2 = index.index_of_index('indexes/inverted_index.txt')
index.write_mapping_to_file('lexicons/index_of_main_index.txt', seek2)

mapping = index.index_of_index('indexes/2gram_index.txt')
# write it to a file
index.write_mapping_to_file('lexicons/index_of_2_gram_index.txt', mapping)


# compare('indexes/unw_doc_to_tf.txt', 'indexes/munw_doc_to_tf.txt')
# compare('indexes/tf_order_index.txt', 'indexes/mtf_order_index.txt')
# compare('indexes/tf_order_2gram_index.txt', 'indexes/mtf_order_2gram_index.txt')
# print('\n\n\n')
# for token in i:
#     print(f"{token}:{i[token][0]._token_count}")

# doc2_wts = ranking.get_doc_to_tfwt(2, "testdoc_to_tf.txt")
# print(doc2_wts)
# intersection = ["car", "insurance"]
# score = ranking.calc_doc_score(intersection, doc2_wts)
# print(score)

# ALSO HAVE TO DEAL WITH BROKEN HTMLLLLLL

# id_url_map = search.get_doc_id_to_url_map(idurlmap_path)
# search.search()

        



