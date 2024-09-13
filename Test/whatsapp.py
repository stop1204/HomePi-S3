"""
curl -i -X POST \
  https://graph.facebook.com/v20.0/411026728762888/messages \
  -H 'Authorization: Bearer <API KEY>' \
  -H 'Content-Type: application/json' \
  -d '{ "messaging_product": "whatsapp", "to": "85253986939", "type": "template", "template": { "name": "raspberry", "language": { "code": "en_US" } } }'
"""

import requests
import json

url = 'https://graph.facebook.com/v20.0/411026728762888/messages'


access_token = 'EAAFgHvw8d80BO1pv8PeSBVBRBlFq0ayZCD7ZAcWUeDZCMyeZA4KCL5ShKRZATykmTvFGJRfxqAk3SwZA6gcjKkVYJoWzilvS6rhbQd8INjjJyOzhEhHcuQVZAjD9WgHcDSswZAOjZA7qJWM4m7ugZCLPFICYaylZCcnaZAHZCDeZB3EyvX6rZB87cVsI27wx2SQdPVIsa1tl1wO0ZCsU3tgHS3Dttc14C36yOkwZD'

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}
template_name = 'raspberry'
payload = {
    'messaging_product': 'whatsapp',
    'to': '85253986939',
    'type': 'template',
    'template': {
        'name': f'{template_name}',
        'language': {
            'code': 'en' # or 'en_US'
        }
    }
}


response = requests.post(url, headers=headers, data=json.dumps(payload))


print(response.status_code)
print(response.text)
"""
200
{"messaging_product":"whatsapp","contacts":[{"input":"85253986939","wa_id":"85253986939"}],"messages":[{"id":"wamid.HBgLODUyNTM5ODY5MzkVAgARGBJCMTc5NTBCOTUwNEJGMjk5NEUA","message_status":"accepted"}]}

"""