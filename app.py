from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

app = Flask(__name__)

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

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    filings = []
    for row in soup.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) > 3:
            filing_date = cols[3].text.strip()
            form_type = cols[0].text.strip()
            filings.append({'date': filing_date, 'type': form_type})

    return jsonify(filings)

if __name__ == '__main__':
    app.run(debug=True)
