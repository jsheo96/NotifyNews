from json import dumps
from httplib2 import Http
import json

def send_message(message):
    with open('secret.json','r') as f:
        j = json.load(f)
    space_id = j['space_id']
    key = j['key']
    token = j['token']
    threadKey = j['threadKey']
    url = f'https://chat.googleapis.com/v1/spaces/{space_id}/messages?' \
          f'key={key}&' \
          f'token={token}&' \
          f'threadKey={threadKey}&' \
          'messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD'
    bot_message = {
        'text': message}
    message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
    http_obj = Http()
    response = http_obj.request(
        uri=url,
        method='POST',
        headers=message_headers,
        body=dumps(bot_message),
    )

if __name__ == '__main__':
    send_message('test message')