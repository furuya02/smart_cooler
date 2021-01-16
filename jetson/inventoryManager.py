# -*- coding: utf-8 -*-
"""
在庫管理クラス
"""

import boto3
from boto3.session import Session

class InventoryManager():
	def __init__(self, session, region, tableName):
		# 商品一覧
		self.__scan_dynamo_db(session, region, tableName)
		# 在庫数初期化
		self.__stock = [0] * len(self.__products)

	# DynamoDBから商品一覧を取得する
	def __scan_dynamo_db(self, session, region, tableName):
		dynamodb = session.resource('dynamodb', region_name=region)
		table = dynamodb.Table(tableName)
		response = table.scan()

		array = []
		for item in response["Items"]:
			array.append({"id":item["id"], "short_name":item["ShortName"], "full_name":item["FullName"], "price":item["Price"]})

		# idでソート	
		self.__products = sorted(array, key=lambda x:x['id'])

	def __getIndex(self, short_name):
		for i, product in enumerate(self.__products):
			if(product["short_name"] == short_name):
				return i
		return -1
	
	def getStock(self):
		return self.__stock.copy()

	def setStock(self, short_names):
		self.__stock = [0] * len(self.__products)
		for short_name in short_names:
			index = self.__getIndex(short_name)
			self.__stock[index] += 1
	
	def get_full_name(self, index):
		return self.__products[index]["full_name"]

	def get_short_name(self, index):
		return self.__products[index]["short_name"]

	def get_price(self, index):
		return int(self.__products[index]["price"])

	@property
	def short_names(self):
		result = []
		for item in self.__products:
			result.append(item["short_name"])
		return result