import numpy as np
import itertools

from konlpy.tag import Okt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class KeywordCreator:
    model_path = "data/model/keyword/keybert"

    def create_keyword(self, doc, model_path="data/model/keyword/keybert"):
        # doc = """
        # 토마토는 맛있는 과일이다.
        # 과일에는 사과, 귤, 토마토, 망고, 애플망고 등이 있다.
        # 토마토는 과일 중에서도 으뜸으로 여러가지 종류로 시중에 판매되고 있다.
        # 예를 들면, 토마토 주스, 토마토 잼, 익힌 토마토 등이 있다.
        # 최근에는 토마토 축제도 많이 열리고 있으며, 토마토를 이용한 질병치료도 활성화되고 있다.
        # """

        okt = Okt()

        tokenized_doc = okt.pos(doc)
        tokenized_nouns = ' '.join([word[0] for word in tokenized_doc if word[1] == 'Noun'])

        print('품사 태깅 10개만 출력 :', tokenized_doc[:10])
        print('명사 추출 :', tokenized_nouns)

        n_gram_range = (1, 1)

        count = CountVectorizer(ngram_range=n_gram_range).fit([tokenized_nouns])
        candidates = count.get_feature_names_out()

        print('단어 개수 :', len(candidates))
        print('단어 다섯개만 출력 :', candidates[:5])

        #model = SentenceTransformer('sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens')
        #model.save(model_path)
        model = SentenceTransformer(model_path)
        doc_embedding = model.encode([doc])
        candidate_embeddings = model.encode(candidates)

        top_n = 2
        keywords = self.mmr(doc_embedding, candidate_embeddings, candidates, top_n=top_n, diversity=0.1)
        return keywords

    def mmr(self, doc_embedding, candidate_embeddings, words, top_n, diversity):
        word_doc_similarity = cosine_similarity(candidate_embeddings, doc_embedding)

        word_similarity = cosine_similarity(candidate_embeddings)

        keywords_idx = [np.argmax(word_doc_similarity)]

        candidates_idx = [i for i in range(len(words)) if i != keywords_idx[0]]

        for _ in range(top_n - 1):
            candidate_similarities = word_doc_similarity[candidates_idx, :]
            target_similarities = np.max(word_similarity[candidates_idx][:, keywords_idx], axis=1)

            # MMR
            mmr = (1 - diversity) * candidate_similarities - diversity * target_similarities.reshape(-1, 1)
            mmr_idx = candidates_idx[np.argmax(mmr)]

            keywords_idx.append(mmr_idx)
            candidates_idx.remove(mmr_idx)

        return [words[idx] for idx in keywords_idx]