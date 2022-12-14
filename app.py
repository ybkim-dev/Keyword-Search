from flask import Flask, request, jsonify, render_template, redirect, url_for, flash

from KeywordCreator import KeywordCreator
from WordExpander import WordExpander

from elasticsearch import Elasticsearch
from elasticsearch import helpers

es = Elasticsearch("http://127.0.0.1:9200")

app = Flask(__name__)

keyword_creator = KeywordCreator()
word_expander = WordExpander()
model = word_expander.get_model()
index_name = 'capstone'

app.secret_key = 'test'

# index 생성 (처음에만 실행시켜주면 index를 생성하고 그 후부터는 데이터를 바로 저장할 수 있음)
def make_index(index_name):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    es.indices.create(index=index_name,
                      body={
                          "settings" : {
                              "analysis" : {
                                  "analyzer" : {
                                      "nori_analyzer" : {
                                          "tokenizer" : "nori_tokenizer"
                                      }
                                  }
                              }
                          },

                          "mappings": {
                              "properties": {
                                  "content": {
                                      "type": "text",
                                      "analyzer": "nori_analyzer"

                                  },
                                  "keywords": {
                                      "type": "keyword",
                                      "fields": {
                                          "keyword": {
                                              "type": "keyword"
                                          }
                                      }
                                  }
                              }
                          }
                      })


#초기 세팅에는 make_index 주석을 풀어야 함
#make_index(index_name)
@app.route('/', methods=['GET'])
def main_page():
    return render_template('index.html')

# 새로운 글 저장하는 페이지
@app.route('/article/view/new', methods=['GET'])
def enroll_document_page():
    return render_template('new_article_view.html')

# 새로운 글 저장하는 API
@app.route('/article', methods=['POST'])
def save_document():
    data_doc = request.form['doc']
    # 키워드를 추출
    keyword = keyword_creator.create_keyword(data_doc)
    # elastic search 에 저장
    doc = {}
    doc["content"] = data_doc
    doc["keywords"] = keyword

    es.index(index=index_name, body=doc)
    # To elastic search
    flash("키워드 : " + keyword[0] + ", " + keyword[1])
    return redirect(url_for('enroll_document_page'))


@app.route('/search', methods=['POST'])
def search():
    view_list = []
    query = request.form['query']
    # elastic search에서 상위 1개 데이터 검색해오기
    try:
        search_result = es.search(index=index_name,
                              body={'from': 0, 'size': 100, 'query': {'match': {'content': query}}}
                              )['hits']['hits'][0]
    except:
        return render_template("article_list.html", view_list=view_list)

    # 어떤 검색어를 통해 검색되었는지 확인
    search_result["searchedBy"] = query
    # Word2Vec 모델을 사용해서 단어 확장
    expand_results = word_expander.expand(model, search_result['_source']["keywords"])
    # elastic search에서 각 expand_results의 원소별로 돌면서 데이터 검색해오기
    for expand_result in expand_results:
        # elastic search 에서 검색
        elastic_result = es.search(index=index_name,
                                   body={'from': 0, 'size': 100, 'query': {'match': {'content': expand_result}}}
                                   )['hits']['hits']

        # 어떤 검색어를 통해 검색되었는지 확인
        for result in elastic_result:
            result["searchedBy"] = expand_result

        view_list.extend(elastic_result)
    # ElasticSearch가 제공해주는 검색 점수를 바탕으로 정렬
    view_list.sort(key=lambda x: x["_score"])
    # 맨 앞에 원래 검색 결과 1개 추가
    view_list.insert(0, search_result)
    return render_template("article_list.html", view_list=view_list)


"""
기본 검색 방법과 비교를 위한 router
"""


@app.route('/search-vanila', methods=['GET'])
def vanila_main_page():
    return render_template('index-vanila.html')


@app.route('/search-vanila', methods=['POST'])
def vanila_search():
    view_list = []
    query = request.form['query']

    expand_results = word_expander.expand(model, [query])

    # elastic search에서 각 expand_results의 원소별로 돌면서 데이터 검색해오기
    for expand_result in expand_results:
        # elastic search 에서 검색
        elastic_result = es.search(index=index_name,
                                   body={'from': 0, 'size': 100, 'query': {'match': {'content': expand_result}}}
                                   )['hits']['hits']

        # 어떤 검색어를 통해 검색되었는지 확인
        for result in elastic_result:
            result["searchedBy"] = expand_result

        view_list.extend(elastic_result)

    view_list.sort(key=lambda x: x["_score"])
    return render_template("article_list.html", view_list=view_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
