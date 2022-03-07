
import os
from collections import OrderedDict
import re

DEBUG = False

def get_tf(cur_posting):
    second_colon = False
    for i in range(len(cur_posting)):
        if cur_posting[i] == ':':
            if second_colon:
                break
            second_colon = True 
    # returns f' {int}'
    return cur_posting[i+1:].strip('}')

def get_docID(cur_posting):
    return int(cur_posting[len('{_docId": '):].split(',')[0])


def nway_merge_plists(posting_lists):
    res = ''
    
    if DEBUG:
        for num, l in enumerate(posting_lists):
            print(f'{num} : {l}')

    # ptrs[i] = info about the current posting in posting_list[i]
    ptrs = {i: [0, get_tf(posting_lists[i][0])] for i in range(len(posting_lists))}            # ptrs[i][0] = the current posting index in posting_list[i]
                                                                      # ptrs[i][1] = the tf for the current posting 
    # for i in range(2):
    while len(ptrs) > 1:
        if DEBUG:
            print('========= ptrs ==========')
            for key, item in ptrs.items():
                print(f'{key}   cur_index: {item[0]}, cur_posting: {item[1]}')
            print()

        # get the next min posting
        max_plst = min(ptrs.keys())
        max_tf = ptrs[max_plst][1]

        for plist, info in ptrs.items():
            cur_pindex, cur_tf = info[0], info[1]
            if cur_tf == max_tf:
                cur_docID = get_docID(posting_lists[plist][ptrs[plist][0]])
                max_docID = get_docID(posting_lists[max_plst][ptrs[max_plst][0]])
                _, max_tf, max_plst = min((cur_docID, cur_tf, plist), (max_docID, max_tf, max_plst))
            elif float(cur_tf) > float(max_tf):
                max_plst = plist
                max_tf = cur_tf
        
        if DEBUG:
            print(f'    Posting List with the min tf ({max_tf}): {max_plst}')
            print()

        # append min posting
        res += posting_lists[max_plst][ptrs[max_plst][0]] + '|'

        # advance pointer for that posting list
        ptrs[max_plst][0] += 1
        min_pindex = ptrs[max_plst][0]

        # remove if pointer is beyond its array
        if min_pindex > len(posting_lists[max_plst])-1:
            del ptrs[max_plst]
        else:
            # pull out the tf from the posting list 
            ptrs[max_plst][1] = get_tf(posting_lists[max_plst][min_pindex])

    # merge the last one
    last_plist = next(iter(ptrs))
    start_index = ptrs[last_plist][0]

    if DEBUG:
        print("========== last_plist to merge: ===========")
        print(f'{last_plist}: {posting_lists[last_plist][start_index:]}')
    for posting in posting_lists[last_plist][start_index:]:
        res += posting + '|'

    return res[:-1]



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


def merge_pindexes(base_dir, final_index_path):
    # opened_file_arr[x] = (pathname, opened file object)
    opened_file_arr = []

    # iterate over directory and open all partial index files, add them to opened_file_arr
    for page in os.scandir(base_dir):  
        if page.is_file() and re.match(r'.*index', page.path) and not re.match(r'.*\.DS_Store', page.path):                      # make sure that you only open correctly named files and not hidden files (.DSStore)
            opened_file_arr.append((page.path, open(page.path, 'r', encoding="utf_8")))

    # stop early
    if len(opened_file_arr) == 1:
        os.rename(opened_file_arr[0][0], final_index_path)
        return

    pindex_count = len(opened_file_arr)       

    if DEBUG:
        print(f'Files in {base_dir}:')
        for f in opened_file_arr:
            print(f[0])

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
        plists_to_merge = []
        
        for f in mintoken_files:
            # add partial doc_freq to merged_docfreq
            merged_docfreq += cur_docfreq_dict[f]

            # get posting lists that need to be merged
            open_file = opened_file_arr[f][1]
            plists_to_merge.append(open_file.readline().strip().split('|'))

            # # merge posting lists
            # merged_postingstr += open_file.readline().strip() + '|'

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

        merged_postingstr = nway_merge_plists(plists_to_merge)

        if DEBUG:
            print(str(merged_docfreq) + '| ') 
        final_index.write(str(merged_docfreq) + '| ' + merged_postingstr + '\n')

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

if __name__ == "__main__":

    plist1 = '{"_docId": 1859, "_token_count": 3.1}'
 
    plist2 = '{"_docId": 522, "_token_count": 10.9}|{"_docId": 930, "_token_count": 9}|{"_docId": 1092, "_token_count": 2}'
    plist3 = '{"_docId": 3659, "_token_count": 10.9}|{"_docId": 4020, "_token_count": 4}'

    lists_to_merge = []
    lists_to_merge.append(plist1.strip().split('|'))
    lists_to_merge.append(plist2.strip().split('|'))
    lists_to_merge.append(plist3.strip().split('|'))
    for l in lists_to_merge:
        print(l)

    print()


    print('FINAL: ' + nway_merge_plists(lists_to_merge))

    # plist1 = '{"_docId": 1859, "_token_count": 9}|{"_docId": 1092, "_token_count": 7}'
 
    # plist2 = '{"_docId": 522, "_token_count": 10}|{"_docId": 930, "_token_count": 8}'
    # plist3 = '{"_docId": 4020, "_token_count": 4}|{"_docId": 3659, "_token_count": 3}'

    # lists_to_merge = []
    # lists_to_merge.append(plist1.strip().split('|'))
    # lists_to_merge.append(plist2.strip().split('|'))
    # lists_to_merge.append(plist3.strip().split('|'))
    # for l in lists_to_merge:
    #     print(l)

    # print()


    # print('FINAL: ' + nway_merge_plists(lists_to_merge))