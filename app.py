from flask import Flask

from KeywordCreator import KeywordCreator

app = Flask(__name__)

keyword_creator = KeywordCreator()


@app.route('/')
def hello_world():  # put application's code here
    keyword = keyword_creator.create_keyword()
    print(keyword)
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
