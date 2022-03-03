
import os
from collections import OrderedDict
import re

DEBUG = False

def get_next_token_and_docfreq(open_file):
    next_token = ''
    cur_char = open_file.read(1)
    
    # get token: advance pointer char by char
    while cur_char != '|' and cur_char != '':
        next_token += cur_char
        cur_char = open_file.read(1)

    # get doc_freq
    next_docfreq = ''
    cur_char = open_file.read(1)
    while cur_char != '|' and cur_char != '':
        next_docfreq += cur_char
        cur_char = open_file.read(1)

    # for error checking
    if next_docfreq == '':
        next_docfreq = None
    else:
        next_docfreq = int(next_docfreq)

    return next_token, next_docfreq


def merge_pindexes(base_dir, final_index_path='merged_index.txt'):
    # opened_file_arr[x] = (pathname, opened file object)
    opened_file_arr = []

    # iterate over directory and open all partial index files, add them to opened_file_arr
    for page in os.scandir(base_dir):  
        if page.is_file() and re.match(r'.*index', page.path):                      # make sure that you only open correctly named files and not hidden files (.DSStore)
            opened_file_arr.append((page.path, open(page.path, 'r', encoding="utf_8")))

    # stop early
    if len(opened_file_arr) == 1:
        os.rename(opened_file_arr[0][0], final_index_path)
        return

    # sort so that pindex files are in order of doc_id, for some reason scandir scans in an arbitrary order
    opened_file_arr.sort(key=lambda a: a[0])
    pindex_count = len(opened_file_arr)       

    if DEBUG:
        print(f'Files in {base_dir}:')
        for f in opened_file_arr:
            print(f[0])

    # cur_word_dict has to be sorted in order of fileno so that merging postings is easy (b/c each doc range is in order by fileno)
    cur_token_dict = OrderedDict()   # <fileno: cur_token>
    cur_docfreq_dict = dict()        # <cur_token: docfreq>
    final_index = open(final_index_path, 'w')

    # initialize: get the first set of cur_tokens
    for i in range(pindex_count):
        filename, file = opened_file_arr[i]

        if DEBUG:
            print(f"READING file {filename}")

        cur_token_dict[i], cur_docfreq_dict[i] = get_next_token_and_docfreq(file)

        if DEBUG:
            print(f'token={cur_token_dict[i]}, freq={cur_docfreq_dict[i]}')
            print()

    # continuously obtain the next set of cur_tokens -- break if only 1 file still has unmerged tokens
    while len(cur_token_dict) > 1:
        if DEBUG:
            print(f'cur_token_dict = {cur_token_dict}')
            print(f"cur_docfreq_dict = {cur_docfreq_dict}")

        # initialize the min to the first word in cur_token_dict
        first_entry = next(iter(cur_token_dict))
        min_token = cur_token_dict[first_entry]
        mintoken_files = [first_entry]

        # find the min_token out of cur_token_dict and track the file(s) that it appears in 
        for i, w in cur_token_dict.items():
            if i == first_entry:    # skip the first entry because that is already the min
                continue
            if w < min_token:
                min_token = w
                mintoken_files = [i]
            elif w == min_token:
                mintoken_files.append(i)

        # write the token to the final index
        final_index.write(min_token + '|')
        if DEBUG:
            print(f"============Files that contain the min_word ({min_token})=====================")
            for fileno in mintoken_files:
                print(f'    {opened_file_arr[fileno][0]}')  
            print()
            print(f"    ==Advancing pointers for files that contained the token==")

        # merge docfreq and posting lists -- from each opened file obj that contained the min_token, append its postings to the posting list
        merged_postingstr = ''
        merged_docfreq = 0
        for f in mintoken_files:
            # add partial doc_freq to merged_docfreq
            merged_docfreq += cur_docfreq_dict[f]
            open_file = opened_file_arr[f][1]

            # append postings to merged posting list
            merged_postingstr += open_file.readline().strip() + '|'

            # advance the ptr, get to the next token (on the next line)
            next_token, next_doc_freq = get_next_token_and_docfreq(open_file)
            cur_token_dict[f] = next_token
            cur_docfreq_dict[f] = next_doc_freq

            if DEBUG:
                print(f'        next_token for doc {f}: {cur_token_dict[f]}')

            # remove file from cur_word_dict if EOF reached
            if cur_token_dict[f] == '':
                del cur_token_dict[f]
                del cur_docfreq_dict[f]

        if DEBUG:
            print() 

        final_index.write(str(merged_docfreq) + '|' + merged_postingstr[:-1] + '\n')

    # this shouldn't happen
    if len(cur_token_dict) > 1:
        raise Exception("len(cur_word_dict) is supposed to be <=1 after exiting the loop")
    elif len(cur_token_dict) == 1:
        last_fileno, last_cur_word = next(iter(cur_token_dict.items()))
        last_openfile = opened_file_arr[last_fileno][1]
        final_index.write(last_cur_word + '|' + str(cur_docfreq_dict[last_fileno]) + '|')
        final_index.write(last_openfile.read())

    for filename, file in opened_file_arr:
        file.close()
    final_index.close()

