# -*- coding: utf-8 -*-
"""
CognitoのPoolIdでSessionを取得する
"""

import boto3
from boto3.session import Session

def createSession(poolId, region):
	client = boto3.client('cognito-identity', region)
	resp =  client.get_id(IdentityPoolId = poolId)
	identityId = client.get_credentials_for_identity(IdentityId=resp['IdentityId'])
	secretKey = identityId['Credentials']['SecretKey']
	accessKey = identityId['Credentials']['AccessKeyId']
	token = identityId['Credentials']['SessionToken']
	return boto3.Session(aws_access_key_id = accessKey, aws_secret_access_key = secretKey, aws_session_token = token)
