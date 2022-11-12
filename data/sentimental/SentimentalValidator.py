# KNU 한국어 감성사전
#-*-coding:utf-8-*-

import json

class SentimentalValidator():
	def SentimentalValidator(self):
		with open('SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
			self.data = json.load(f)

	def isSentimental(self, word):
		for i in range(len(self.data)):
			if(self.data[i]['word'] == word):
				return True
		return False