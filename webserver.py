from flask import Flask, render_template, jsonify, request, redirect, url_for
import json
import os
from datetime import datetime
import requests
from googlewebhook import send_message

app = Flask(__name__)

def load_config():
    """Load configuration from config.json"""
    with open('config.json', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """Save configuration to config.json"""
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def get_news_from_api(query, max_news=3):
    """Fetch news from Naver API"""
    if not os.path.exists('secret.json'):
        return {'error': 'secret.json not found. Please ask administrator.'}
    
    try:
        with open('secret.json') as f:
            secret = json.load(f)
        
        clientId = secret['clientId']
        clientSecret = secret['clientSecret']
        url = "https://openapi.naver.com/v1/search/news?"
        
        queryString = 'query=' + query
        header = {
            'X-Naver-Client-Id': clientId,
            'X-Naver-Client-Secret': clientSecret
        }
        
        r = requests.get(url + queryString, headers=header)
        j = json.loads(r.text)
        
        if 'items' in j:
            return j['items'][:max_news]
        else:
            return {'error': 'No items found in API response'}
    except Exception as e:
        return {'error': str(e)}

def get_previous_links():
    """Get previously processed links"""
    try:
        with open('previous_links.txt', 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

def add_to_previous_links(link):
    """Add link to previous links file"""
    with open('previous_links.txt', 'a') as f:
        f.write(link + '\n')

@app.route('/')
def index():
    """Main dashboard"""
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/api/news')
def api_news():
    """API endpoint to get current news"""
    config = load_config()
    query = config.get('query', '')
    max_news = config.get('max_news', 3)
    
    if not query:
        return jsonify({'error': 'No query configured'})
    
    news_items = get_news_from_api(query, max_news)
    if isinstance(news_items, dict) and 'error' in news_items:
        return jsonify(news_items)
    
    previous_links = get_previous_links()
    
    # Filter out already seen news
    new_items = []
    for item in news_items:
        if item['link'] not in previous_links:
            new_items.append(item)
    
    return jsonify({
        'total_items': len(news_items),
        'new_items': len(new_items),
        'news': new_items
    })

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """API endpoint to get/set configuration"""
    if request.method == 'GET':
        return jsonify(load_config())
    
    elif request.method == 'POST':
        try:
            new_config = request.json
            save_config(new_config)
            return jsonify({'success': True, 'message': 'Configuration updated'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@app.route('/api/fetch-and-send', methods=['POST'])
def api_fetch_and_send():
    """API endpoint to manually trigger news fetch and send"""
    config = load_config()
    query = config.get('query', '')
    max_news = config.get('max_news', 3)
    
    if not query:
        return jsonify({'success': False, 'error': 'No query configured'})
    
    news_items = get_news_from_api(query, max_news)
    if isinstance(news_items, dict) and 'error' in news_items:
        return jsonify({'success': False, 'error': news_items['error']})
    
    previous_links = get_previous_links()
    sent_count = 0
    
    for item in news_items:
        title = item['title']
        link = item['link']
        
        if link not in previous_links:
            try:
                message = title + '\n' + link
                send_message(message)
                add_to_previous_links(link)
                sent_count += 1
            except Exception as e:
                return jsonify({'success': False, 'error': f'Failed to send message: {str(e)}'})
    
    return jsonify({
        'success': True,
        'message': f'Sent {sent_count} new news items',
        'sent_count': sent_count
    })

@app.route('/api/history')
def api_history():
    """API endpoint to get news history"""
    previous_links = get_previous_links()
    return jsonify({
        'total_links': len(previous_links),
        'links': previous_links[-20:]  # Show last 20 links
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(debug=True, host='0.0.0.0', port=5000)