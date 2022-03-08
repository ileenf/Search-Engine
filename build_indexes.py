import index
import merge_pindex
import sys
import os

TRACE = False
def trace_print(s):
    if TRACE:
        print(s)

base_dir = './DEV'
p_inv_basedir = index.DIRECTORY_DICT['inv']
p_2gram_basedir = index.DIRECTORY_DICT['2gram']


if __name__ == '__main__':

    if len(sys.argv) > 2:
        print('only 1 extra argument should be provided')
        exit()
    
    if len(sys.argv) == 2 and sys.argv[1] == '-trace':
        index.TRACE = True
        merge_pindex.TRACE = True

    os.makedirs('indexes/inv_pindexes/')
    os.makedirs('indexes/2gram_pindexes/')
    os.makedirs('auxiliary')
    os.makedirs('lexicons')

    # build inverted index and 2 gram index
    id_url_map, doc_to_tokens, doc_to_two_grams = index.build_indexes(base_dir)
    trace_print('Building indexes/inverted_index.txt, indexes/2gram_index.txt')
    merge_pindex.merge_pindexes(p_inv_basedir, 'indexes/inverted_index.txt')
    merge_pindex.merge_pindexes(p_2gram_basedir, 'indexes/2gram_index.txt')

    # build id url map
    index.write_mapping_to_file('auxiliary/id_url_map.txt', id_url_map)

    # build doc to tf index
    index.write_doc_to_tokens_file(doc_to_tokens, 'auxiliary/doc_to_tf.txt')
    index.write_doc_to_tokens_file(doc_to_two_grams, 'auxiliary/doc_to_tf_2grams.txt')

    # build index of index for main indexes
    mapping = index.index_of_index('indexes/2gram_index.txt')
    index.write_mapping_to_file('lexicons/index_of_2_gram_index.txt', mapping)

    mapping = index.index_of_index('indexes/inverted_index.txt')
    index.write_mapping_to_file('lexicons/index_of_inverted_index.txt', mapping)

    # build index of index for doc to tf indexes
    mapping = index.index_of_index('auxiliary/doc_to_tf_2grams.txt')
    index.write_mapping_to_file('lexicons/index_of_doc_to_tf_2grams.txt', mapping)

    mapping = index.index_of_index('auxiliary/doc_to_tf.txt')
    index.write_mapping_to_file('lexicons/index_of_doc_to_tf.txt', mapping)