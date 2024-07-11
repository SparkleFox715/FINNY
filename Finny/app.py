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

    summary = generate_analytical_summary(filings)
    return jsonify({'filings': filings, 'summary': summary})

@app.route('/fetch-filing-data', methods=['POST'])
def fetch_filing_data():
    filing_url = request.json['filing_url']
    headers = {'User-Agent': 'Mozilla/5.0'}

    content = fetch_sec_data_from_url(filing_url, headers)
    if content is None:
        return jsonify({'error': 'Failed to fetch filing data. Please try again later.'}), 500

    soup = BeautifulSoup(content, 'html.parser')
    filing_summary = interpret_filing(soup)
    return jsonify({'summary': filing_summary})

def generate_analytical_summary(filings):
    if not filings:
        return "No filings available to summarize."
    
    summary = ""
    insider_trading = any(filing['type'] == '4' for filing in filings)
    earnings_reports = [filing for filing in filings if '10-Q' in filing['type'] or '10-K' in filing['type']]
    significant_filings = [filing for filing in filings if '8-K' in filing['type']]

    if insider_trading:
        summary += "Recent insider trading activity detected.\n"
    if earnings_reports:
        summary += f"Latest earnings reports:\n"
        for report in earnings_reports[:3]:  # Limit to the most recent 3
            summary += f" - {report['type']} filed on {report['date']} (Link: {report['link']})\n"
    if significant_filings:
        summary += f"Significant filings (e.g., 8-K) include:\n"
        for filing in significant_filings[:3]:  # Limit to the most recent 3
            summary += f" - {filing['type']} filed on {filing['date']} (Link: {filing['link']})\n"
    
    summary += f"\nTotal filings: {len(filings)}.\n"
    form_types = {}
    for filing in filings:
        form_types[filing['type']] = form_types.get(filing['type'], 0) + 1
    summary += "Filing types distribution:\n"
    for form_type, count in form_types.items():
        summary += f" - {form_type}: {count}\n"
    
    return summary

def interpret_filing(soup):
    # Extract some example information for interpretation
    document = soup.find('document')
    if document:
        text = document.get_text()
        if len(text) > 500:
            return text[:500] + '...'
        return text
    return "No detailed information available for this filing."

if __name__ == '__main__':
    app.run(debug=True)
