import math

def calculate_cosine_similarity(weights):
    count = 0
    for weight in weights:
        count += (weight**2)
    return math.sqrt(count)

def query_ltc_ranking(query_terms: dict, doc_freq_map: dict):
    term_to_score = dict()
    normalized_scores = dict()

    for term, term_freq in query_terms.items():
        term_freq_weight = 1 + math.log10(term_freq)
        inverted_doc_freq = math.log10(55393/doc_freq_map[term])
        score_weight = term_freq_weight * inverted_doc_freq
        term_to_score[term] = score_weight

    cosine_similarity = calculate_cosine_similarity(term_to_score.values())
    for term, score in term_to_score.items():
        normalized = score / cosine_similarity
        normalized_scores[term] = normalized

    return normalized_scores


score = query_ltc_ranking({'best': 1, 'car':1, 'insurance': 1}, {'best': 50000, 'car': 10000, 'insurance': 1000})
print(score)




