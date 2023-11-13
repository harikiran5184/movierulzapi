from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

def scrape_data(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example: Extracting data from HTML elements
        title = soup.title.string
        paragraphs = [p.get_text() for p in soup.find_all('p')]

        # Example: Creating a data object
        data = {
            'title': title,
            'paragraphs': paragraphs,
        }

        return data
    except Exception as e:
        raise e

@app.route('/scrape')
def scrape_route():
    target_url = 'https://www.google.com/'
    try:
        data = scrape_data(target_url)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
