# -*- coding: utf-8 -*-
"""
AmazonPayによる決済クラス
"""
import json
import boto3
from boto3.session import Session

class AmazonPay():
	def __init__(self, session, region):
		self.__client = session.client('lambda', region)
		self.__functionName = "smart_cooler_amazon_pay"
	
	def scan(self, scanData):
		query = {
			"command": "scan",
			"payload": {
				"scanData": scanData
			}
		}
		response = self.__client.invoke(
			FunctionName = self.__functionName,
			InvocationType='RequestResponse',
			LogType='Tail',
			Payload= json.dumps(query)
		)
		body = json.loads(response['Payload'].read()) 
		print("body:", body)
		return body

	def charge(self, chargePermissionId, amount, merchantNote, merchantStoerName, merchantOrderId):
		query = {
			"command": "charge",
			"payload": {
				"chargePermissionId": chargePermissionId,
				"amount": amount,
				"merchantNote": merchantNote,
				"merchantStoerName": merchantStoerName,
				"merchantOrderId": merchantOrderId
			}
		}
		response = self.__client.invoke(
			FunctionName = self.__functionName,
			InvocationType='RequestResponse',
			LogType='Tail',
			Payload= json.dumps(query)
		)
		body = json.loads(response['Payload'].read()) 
		print("body:", body)
		return body

