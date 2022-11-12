import gensim

from data.sentimental.SentimentalValidator import SentimentalValidator

sentiment_validator = SentimentalValidator()

class WordExpander:

    def get_model(self):
        korean_model = gensim.models.Word2Vec.load("./data/model/word2vec/korean_model.bin")
        return korean_model

    def expand(self, model, words):
        expanded = []
        for word in words:
            expanded.append(word)
            try:
                if sentiment_validator.isSentimental(word):
                    # 감정 단어인 경우 확장하지 않음
                    continue
                similar_word = model.wv.most_similar(word, topn=1)
                expanded.append(similar_word)
            except:
                continue
        return expanded

# wordExpander = WordExpander()
# model = wordExpander.get_model()
# expand = wordExpander.expand(model, ["락", "페스티벌"])
# print(expand)

