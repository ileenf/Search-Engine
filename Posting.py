class Posting:
    def __init__(self, url, token_count, tot_tokens):
        self._url = url
        self._token_count = token_count
        self._token_freq = token_count / tot_tokens

    def getTokenFreq(self):
        return self._token_freq


    
