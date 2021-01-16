import * as cdk from '@aws-cdk/core';
import dynamodb = require("@aws-cdk/aws-dynamodb");
import * as iam from '@aws-cdk/aws-iam';
import * as cognito from '@aws-cdk/aws-cognito';
import * as lambda from '@aws-cdk/aws-lambda';

export class SmartCoolerStack extends cdk.Stack {
	constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
		super(scope, id, props);
		
		const publicKeyId = new cdk.CfnParameter(this, 'publicKeyId', {
			type: 'String',
			description: 'AmazonPay public Key',
			default: 'XXXXXXXXXXXXXX'
		})

		// DynamoDB
		const db = new dynamodb.Table(this, "Products", {
			tableName: "SmartCoolerProducts",
			partitionKey: {
				name: "id",
				type: dynamodb.AttributeType.NUMBER
			}
		});

		// Lambda
		const lambdaFunction = new lambda.Function( this, 'lambda-function', {
			functionName: 'smart_cooler_amazon_pay',
			runtime: lambda.Runtime.NODEJS_12_X,
			handler: 'index.handler',
			code: lambda.Code.fromAsset('lib/lambda'),
			environment:{
				"PUBLIC_KEY_ID": publicKeyId.valueAsString
			}
		})

		// Cognito
		const poolId = new cognito.CfnIdentityPool(this, 'CognitoIdentityPool', {
			identityPoolName: "SmartCooler",
			allowUnauthenticatedIdentities: true
		});
		const role = new iam.Role(this, 'UnauthenticatedRole', {
			roleName: "SmartCoolerRole",
			assumedBy: new iam.FederatedPrincipal('cognito-identity.amazonaws.com', {
				"StringEquals": { "cognito-identity.amazonaws.com:aud": poolId.ref },
				"ForAnyValue:StringLike": { "cognito-identity.amazonaws.com:amr": "unauthenticated" },
			}, "sts:AssumeRoleWithWebIdentity"),
		});
		role.addToPolicy(new iam.PolicyStatement({
			effect: iam.Effect.ALLOW,
			actions: [
				"dynamodb:Scan"
			],
			resources: [db.tableArn]
		}));
		role.addToPolicy(new iam.PolicyStatement({
			effect: iam.Effect.ALLOW,
			actions: [
				"polly:SynthesizeSpeech"
			],
			resources: ["*"]
		}));
		role.addToPolicy(new iam.PolicyStatement({
			effect: iam.Effect.ALLOW,
			actions: [
				"lambda:InvokeFunction"
			],
			resources: [lambdaFunction.functionArn]
		}));
		new cognito.CfnIdentityPoolRoleAttachment(this, 'DefaultValid', {
			identityPoolId: poolId.ref,
			roles: {
				'unauthenticated': role.roleArn
			}
		});

		new cdk.CfnOutput(this, 'PoolId', {
			value: poolId.ref
		});
	}
}
