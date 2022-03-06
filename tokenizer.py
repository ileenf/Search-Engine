import re
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from collections import defaultdict, Counter

def parse_text(html: str) -> [str]:
    ''' given an html string, pulls text from the following tags:
        <p>, <h1/2/3/4/5/6>, <strong>, <i>, <b>, <u>, <title>, <meta name="author"/"description"/"keywords">
    '''
    tags_to_text = defaultdict(list)

    header_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "title"]
    emphasis_tags = ["strong", "i", "b", "u"]
    text_tags = ["p", "div"]
    soup = BeautifulSoup(html, 'html.parser')

    header_tags_text = soup.find_all(header_tags)
    emphasis_tags_text = soup.find_all(emphasis_tags)
    text_tags_text = soup.find_all(text_tags)
    meta_text = soup.find_all(name="meta", attrs={"name": re.compile(r'^(author|description|keywords)$')})

    if header_tags_text:
        for t in header_tags_text:
            if t.text.strip() != '':
                tokenized_text = tokenize(t.text)
                tags_to_text['headers'].append(tokenized_text)

    if emphasis_tags_text:
        for t in emphasis_tags_text:
            if t.text.strip() != '':
                tokenized_text = tokenize(t.text)
                tags_to_text['emphasis'].append(tokenized_text)

    if text_tags_text:
        for t in text_tags_text:
            if t.text.strip() != '':
                tokenized_text = tokenize(t.text)
                tags_to_text['paragraph'].append(tokenized_text)

    if meta_text:
        for m in meta_text:
            if m.has_attr("content") and m["content"].strip() != '':
                tokenized_text = tokenize(m["content"])
                tags_to_text['meta_content'].append(tokenized_text)

    two_grams = tokenize_two_grams(tags_to_text)
    
    for tag, tokens in tags_to_text.items():
        concatenated_list = []
        for lst in tokens:
            concatenated_list.extend(lst)
        tags_to_text[tag] = Counter(concatenated_list)

    return tags_to_text, two_grams

def tokenize(string) -> [str]:
    ''' given a string, returns list of tokens '''
    ps = PorterStemmer()
    tokens = []
    try:
        words = re.findall(r"[a-zA-Z0-9]+", string)
        for word in words:
            tokens.append(ps.stem(word.lower()))     
        return tokens

    except UnicodeDecodeError:
        return tokens

def tokenize_two_grams(field_tf_map) -> [str]:
    two_grams = []
    for field, list_of_lists in field_tf_map.items():
        for token_list in list_of_lists:
            two_grams.extend(tokenize_two_grams_from_list(token_list))
    return two_grams


def tokenize_two_grams_from_list(token_list) -> [str]:
    two_grams = []
    for i in range(len(token_list)-1):
        two_gram = token_list[i] + token_list[i+1]
        two_grams.append(two_gram)
    return two_grams


