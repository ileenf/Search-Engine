
import os
from collections import OrderedDict
import re
BASE_DIR = 'PartialIndexMergeTesting/pindexes'

DEBUG = True

def get_next_token_and_docfreq(open_file):
    next_token = ''
    cur_char = open_file.read(1)
  

    while cur_char != '|' and cur_char != '':
        next_token += cur_char
        # print(next_token)
        cur_char = open_file.read(1)

    next_docfreq = ''
    cur_char = open_file.read(1)
    while cur_char != '|' and cur_char != '':
        next_docfreq += cur_char
        cur_char = open_file.read(1)

    print(next_token)
    print(next_docfreq)

    if next_docfreq == '':
        next_docfreq = None
    else:
        next_docfreq = int(next_docfreq)

    return next_token, next_docfreq


def merge_pindexes(base_dir, final_index_path='final_index.txt'):
# (pathname, opened file)
    file_arr = []

    # iterate over directory and open all files, add them to an array
    for page in os.scandir(base_dir):  # each file within subdir = webpage
        if page.is_file() and re.match(r'.*index', page.path):
            file_arr.append((page.path, open(page.path, 'r', encoding="utf_8")))


    # stop early
    if len(file_arr) == 1:
        os.rename(file_arr[0][0], final_index_path)
        return


    # so that the indexes are in order of doc_id, for some reason scandir scans in an arbitrary order
    file_arr.sort(key=lambda a: a[0])
    pindex_count = len(file_arr)

    if DEBUG:
        print(f'Files in {base_dir}:')
        for f in file_arr:
            print(f[0])

   
    # <fileno, cur_word>
    # has to be sorted in order of fileno so that merging postings is easy (b/c each doc range is in order by fileno)
    cur_word_dict = OrderedDict()
    cur_docfreq_dict = dict()
    final_index = open(final_index_path, 'w')

    # initialize: get the first set of cur_words
    for i in range(pindex_count):
        filename, file = file_arr[i]

        if DEBUG:
            print(f"READING file {filename}")

        cur_word_dict[i], cur_docfreq_dict[i] = get_next_token_and_docfreq(file)

        if DEBUG:
            print(f'token={cur_word_dict[i]}, freq={cur_docfreq_dict[i]}')
            print()


    # break if only 1 file still has unmerged tokens
    while len(cur_word_dict) > 1:
        print(f'cur_word_dict = {cur_word_dict}')
        print(f"cur_doc_freq_dict = {cur_docfreq_dict}")

        first_entry = next(iter(cur_word_dict))
        min_word = cur_word_dict[first_entry]
        minword_files = [first_entry]

        for i, w in cur_word_dict.items():
            if i == first_entry:    # skip the first entry because that is already the min
                continue
            if w < min_word:
                min_word = w
                minword_files = [i]
            elif w == min_word:
                minword_files.append(i)

        print(f"============Files that contain the min_word ({min_word})=====================")
        for fileno in minword_files:
            print(f'    {file_arr[fileno][0]}')  
        print()
        # write the token to the final index
        final_index.write(min_word + '|')
        

        # from each file that contained the token: append its postings to the posting list
        print(f"    ==Advancing pointers for files that contained the token==")
        merged_postingstr = ''
        merged_docfreq = 0
        for f in minword_files:
            # write the doc_freqs to the final index
            merged_docfreq += cur_docfreq_dict[f]
            open_file = file_arr[f][1]
            merged_postingstr += open_file.readline().strip() + '|'

            # advance the ptr, get to the next token
            next_token, next_doc_freq = get_next_token_and_docfreq(open_file)
            cur_word_dict[f] = next_token
            cur_docfreq_dict[f] = next_doc_freq

            if DEBUG:
                print(f'        next_token for doc {f}: {cur_word_dict[f]}')

            # remove file from cur_word_dict if EOF reached
            if cur_word_dict[f] == '':
                del cur_word_dict[f]
                del cur_docfreq_dict[f]

        if DEBUG:
            print() 
        final_index.write(str(merged_docfreq) + '|' + merged_postingstr[:-1] + '\n')

    # this shouldn't happen
    if len(cur_word_dict) > 1:
        raise Exception("len(cur_word_dict) is supposed to be <=1 after exiting the loop")
    elif len(cur_word_dict) == 1:
        last_fileno, last_cur_word = next(iter(cur_word_dict.items()))
        last_openfile = file_arr[last_fileno][1]
        final_index.write(last_cur_word + '|' + str(cur_docfreq_dict[last_fileno]) + '|')
        final_index.write(last_openfile.read())

    for filename, file in file_arr:
        file.close()

    final_index.close()

