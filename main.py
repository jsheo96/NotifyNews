import requests
import json
import os
import sys
from googlewebhook import send_message

def fetch_and_send_news():
    """Original news fetching functionality"""
    if not os.path.exists('secret.json'):
        print('secret.json not found. please ask administrator.')
        raise FileNotFoundError

    with open('secret.json') as f:
        secret = json.load(f)
    clientId = secret['clientId']
    clientSecret = secret['clientSecret']
    url = "https://openapi.naver.com/v1/search/news?"

    with open('config.json', encoding='utf-8') as f:
        config = json.load(f)
    query = config['query']
    queryString = 'query=' + query
    header = {
        'X-Naver-Client-Id': clientId,
        'X-Naver-Client-Secret': clientSecret
    }
    r = requests.get(url + queryString, headers=header)
    j = json.loads(r.text)
    items = j['items']
    print(r.text)
    max_news = config['max_news']
    
    try:
        with open('previous_links.txt', 'r') as f:
            previous_links = f.readlines()
    except FileNotFoundError:
        previous_links = []
    
    sent_count = 0
    for item in items[:max_news]:
        title = item['title']
        link = item['link']
        if link + '\n' in previous_links:
            continue
        message = title + '\n' + link
        send_message(message)
        sent_count += 1

        with open('previous_links.txt', 'a') as f:
            f.write(link + '\n')
    
    print(f"Sent {sent_count} new news items")
    return sent_count

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'webserver':
        # Start web server
        from webserver import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        # Run original CLI functionality
        fetch_and_send_news()
