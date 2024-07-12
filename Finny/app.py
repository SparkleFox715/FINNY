from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import time

app = Flask(__name__)

def fetch_sec_data_from_url(url, headers, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Attempt {attempt + 1}: Status code {response.status_code}")
                time.sleep(delay)
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1}: Request failed: {e}")
            time.sleep(delay)
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sec-data')
def sec_data():
    return render_template('secData.html')

@app.route('/fetch-sec-data', methods=['POST'])
def fetch_sec_data():
    ticker = request.json['ticker'].upper()
    encoded_ticker = quote(ticker)
    url = f'https://www.sec.gov/cgi-bin/browse-edgar?CIK={encoded_ticker}&action=getcompany&owner=exclude&count=10'
    headers = {'User-Agent': 'Mozilla/5.0'}

    content = fetch_sec_data_from_url(url, headers)
    if content is None:
        return jsonify({'error': 'Failed to fetch data from SEC website. Please try again later.'}), 500

    soup = BeautifulSoup(content, 'html.parser')
    filings = []
    try:
        rows = soup.find_all('tr')[1:]
        if not rows:
            return jsonify({'error': 'No data available for this ticker.'}), 404

        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 3:
                filing_date = cols[3].text.strip() if cols[3] else 'N/A'
                form_type = cols[0].text.strip() if cols[0] else 'N/A'
                link_tag = cols[1].find('a')
                filing_link = 'https://www.sec.gov' + link_tag['href'] if link_tag else '#'
                filings.append({'date': filing_date, 'type': form_type, 'link': filing_link})
    except Exception as e:
        print(f"Error parsing data: {e}")
        return jsonify({'error': 'Error parsing SEC data. Please try again later.'}), 500

    return jsonify({'filings': filings})

@app.route('/fetch-filing-data', methods=['POST'])
def fetch_filing_data():
    filing_url = request.json['filing_url']
    headers = {'User-Agent': 'Mozilla/5.0'}

    content = fetch_sec_data_from_url(filing_url, headers)
    if content is None:
        return jsonify({'error': 'Failed to fetch filing data. Please try again later.'}), 500

    soup = BeautifulSoup(content, 'html.parser')
    document = soup.find('document')
    if document:
        filing_text = document.get_text()
    else:
        filing_text = "No detailed information available for this filing."

    return jsonify({'summary': filing_text})

if __name__ == '__main__':
    app.run(debug=True)
