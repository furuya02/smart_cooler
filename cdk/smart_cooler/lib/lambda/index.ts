const Client = require('@amazonpay/amazon-pay-api-sdk-nodejs');

function dateStr(): string {
	const dt = new Date()
	return String(dt.getTime())
}

function InStoreClient(publicKeyId: string, privateKey: string, sandbox: boolean): any {
	const fs = require('fs');
	const config = {
		'publicKeyId' : publicKeyId,
		'privateKey' : fs.readFileSync(privateKey),
		'region' : 'jp',
		'sandbox' : String(sandbox)
	};
	return new Client.InStoreClient(config);
}

async function scan(client: any, payload: any){
	console.log(`Scan() payload:${JSON.stringify(payload)}`)
	const scanData = payload["scanData"]
	try {
		const result = await client.apiCall({
			method: 'POST',
			urlFragment: 'in-store/merchantScan',
			payload: {
				scanData: scanData,
				scanReferenceId: 'scanReferId'+dateStr(),
				merchantCOE: 'JP',
				ledgerCurrency: 'JPY',
			}
		})
		return {
			statusCode: 200,
			body: JSON.parse(result.body)
		};
	} catch (error) {
		return {
			statusCode: 400,
			body: JSON.parse(error.body)
		};
	}
}

async function charge(client: any, payload: any){
	console.log(`Charge() payload:${JSON.stringify(payload)}`)

	const chargePermissionId = payload["chargePermissionId"]
	const amount = payload["amount"]
	const merchantNote = payload["merchantNote"]
	const merchantStoerName = payload["merchantStoerName"]
	const merchantOrderId = payload["merchantOrderId"]

	try {
		const result = await client.apiCall({
			method: 'POST',
			urlFragment: 'in-store/charge',
			payload: {
				chargePermissionId: chargePermissionId,
				chargeReferenceId: "chargeRefId" + dateStr(),
				chargeTotal : {
				  currencyCode : 'JPY',
				  amount : amount,
				},
				metadata : {
					merchantNote : merchantNote,
					communicationContext : {
						merchantStoreName : merchantStoerName,
						merchantOrderId : merchantOrderId
					}
				}
			}
		})
		console.log(JSON.parse(result.body))
		return {
			statusCode: 200,
			body: JSON.parse(result.body)
		};
	} catch (error) {
		return {
			statusCode: 401,
			body: JSON.parse(error.body)
		};
	}
}

exports.handler = async (event:any) => {
	console.log(JSON.stringify(event));
	const command = event["command"];
	const payload = event["payload"];

	// InstoreClient
	const publicKeyId = process.env.PUBLIC_KEY_ID as string;
	const privateKey = './private.pem';
	const sandbox = true;
	const client = InStoreClient(publicKeyId, privateKey, sandbox);

	switch(command){
		case "scan":
			return await scan(client, payload)
		case "charge":
			return await charge(client, payload)
	}
	return {
		statusCode: 401,
		body: {
			"message": 'coomand not found.'
		}
	};
};


