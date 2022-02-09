import re
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer

# we don't want to exclude stopwords yet
#stop_words = {'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves'}

def parse_text(html: str) -> [str]:
    ''' given an html string, pulls text from the following tags:
        <p>, <h1/2/3/4/5/6>, <strong>, <i>, <b>, <u>, <title>, <meta name="author"/"description"/"keywords">
    '''
    parsed_str = ' '
    tags = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "strong", "i", "b", "u", "title"]
    soup = BeautifulSoup(html, 'html.parser')

    tags_text = soup.find_all(tags)
    meta_text = soup.find_all(name="meta", attrs={"name": re.compile(r'^(author|description|keywords)$')})

    for t in tags_text:
        if t.text.strip() != '':
            parsed_str += t.text + ' '

    for m in meta_text:
        if m.has_attr("content") and m["content"].strip() != '':
            parsed_str += m["content"] + ' '

    return parsed_str

def tokenize(string) -> [str]:
    '''
    given a string, returns list of tokens
    '''
    ps = PorterStemmer()
    tokens = []
    try:
        words = re.findall(r"[a-zA-Z0-9]+(?:[':-][a-zA-Z0-9]+)*", string)
        for word in words:
            tokens.append(ps.stem(word.lower()))     
        return tokens
            
    # Catch Unicode errors
    except UnicodeDecodeError:
        return tokens

