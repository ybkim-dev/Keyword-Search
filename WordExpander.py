import gensim

class WordExpander:

    def get_model(self):
        korean_model = gensim.models.Word2Vec.load("./model/word2vec/korean_model.bin")
        return korean_model

    def expand(self, model, words):
        expanded = []
        for word in words:
            similar_word = model.wv.most_similar(word, topn=1)
            expanded.append(word)
            expanded.append(similar_word)
        return expanded