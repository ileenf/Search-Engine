class Posting:
    def __init__(self, url, token_count, total_tokens):
        self._url = url
        self._token_count = token_count
        self._token_freq = token_count / total_tokens

    def get_token_freq(self):
        return self._token_freq

