# KNU 한국어 감성사전
#-*-coding:utf-8-*-

import json

class SentimentalValidator():
	def isSentimental(self, word):
		with open('data/sentimental/SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
			data = json.load(f)
		# 감성 단어를 확인하고 true / false 반환
		for i in range(len(data)):
			if(data[i]['word'] == word):
				return True
		return False