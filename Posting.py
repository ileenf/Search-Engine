class Posting:

    def __init__(self, doc_id, token_count, total_tokens):
        self._docId = doc_id
        self._token_count = token_count
        self._token_freq = token_count / total_tokens

    def get_token_freq(self):
        return self._token_freq

    def get_docID(self):
        return self._docId      

