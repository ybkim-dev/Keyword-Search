from flask import Flask, request, jsonify

from KeywordCreator import KeywordCreator
from WordExpander import WordExpander

app = Flask(__name__)

keyword_creator = KeywordCreator()
word_expander = WordExpander()
model = word_expander.get_model()


@app.route('/keywords', methods=['POST'])
def save_document():
    data = request.get_json()
    keyword = keyword_creator.create_keyword(data['text'])
    # elastic search 에 저장
    doc = {}
    doc["body"] = data['text']
    doc["keywords"] = keyword
    # To elastic search
    return doc


@app.route('/search', methods=['GET'])
def search(query):
    view_list = []
    # elastic search에서 상위 1개 데이터 검색해오기
    search_result = {'text': "가나다라마바사", 'keywords': ["가나다", "라마바"]}
    expand_results = word_expander.expand(model, search_result["keywords"])
    # elastic search에서 각 expand_results의 원소별로 돌면서 데이터 검색해오기
    elastic_results = []
    for expand_result in expand_results:
        # elastic search 에서 검색
        elastic_result = {'text' : "바바바바바", 'keywords' : ['마마마마','라라라라']}
        view_list.append(elastic_result)
    view_list.sort(key = lambda x : x["score"])
    # 맨 앞에 원래 검색 결과 1개 추가
    view_list.insert(0, search_result)

if __name__ == '__main__':
    app.run()
