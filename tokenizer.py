import re
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from collections import defaultdict, Counter

# we don't want to exclude stopwords yet
#stop_words = {'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves'}

def parse_text(html: str) -> [str]:
    ''' given an html string, pulls text from the following tags:
        <p>, <h1/2/3/4/5/6>, <strong>, <i>, <b>, <u>, <title>, <meta name="author"/"description"/"keywords">
    '''
    parsed_str = ''
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
                parsed_str += t.text + ' '
                tags_to_text['headers'].append(tokenized_text)

    if emphasis_tags_text:
        for t in emphasis_tags_text:
            if t.text.strip() != '':
                tokenized_text = tokenize(t.text)
                parsed_str += t.text + ' '
                tags_to_text['emphasis'].append(tokenized_text)

    if text_tags_text:
        for t in text_tags_text:
            if t.text.strip() != '':
                tokenized_text = tokenize(t.text)
                parsed_str += t.text + ' '
                tags_to_text['paragraph'].append(tokenized_text)

    if meta_text:
        for m in meta_text:
            if m.has_attr("content") and m["content"].strip() != '':
                tokenized_text = tokenize(m["content"])
                tags_to_text['meta_content'].append(tokenized_text)
                parsed_str += m["content"] + ' '

    two_grams = tokenize_two_grams(tags_to_text)
    
    for tag, tokens in tags_to_text.items():
        concatenated_list = []
        for lst in tokens:
            concatenated_list.extend(lst)
        tags_to_text[tag] = Counter(concatenated_list)

    # tags_to_text: {meta_content: {every token that appeared in meta_content: how many times it occurred},
    #                paragraph:    {every token that appeared in paragraphs: how many times it occurred},
    #                etc. }

    return parsed_str, tags_to_text, two_grams

def tokenize(string) -> [str]:
    '''
    given a string, returns list of tokens
    '''
    ps = PorterStemmer()
    tokens = []
    try:
        words = re.findall(r"[a-zA-Z0-9]+", string)
        for word in words:
            tokens.append(ps.stem(word.lower()))     
        return tokens
            
    # Catch Unicode errors
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


