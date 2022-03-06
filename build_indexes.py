import index

base_dir = './DEV'
# build inverted index and 2 gram index

# build doc to tf index

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

# build id url map
mapping = index.build_id_url_map(base_dir)
index.write_mapping_to_file('auxiliary/id_url_map.txt', mapping)