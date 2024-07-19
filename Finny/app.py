from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import time
import yfinance as yahFin

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

@app.route('/finance-data')
def finance_data():
    return render_template('financeData.html')

@app.route('/fetch-finance-data', methods=['POST'])
def fetch_finance_data():
    ticker = request.json['ticker'].upper()
    data = fetch_yahoo_data(ticker)
    if data:
        return jsonify(data)
    else:
        return jsonify({'error': 'Failed to fetch financial data. Please try again later.'}), 500

def fetch_yahoo_data(symbol):
    generalInfo = yahFin.Ticker(symbol)
    info = {
        'TrailingPE': generalInfo.info.get('trailingPE', 'N/A'),
        'ForwardPE': generalInfo.info.get('forwardPE', 'N/A'),
        'TrailingEPS': generalInfo.info.get('trailingEps', 'N/A'),
        'ForwardEPS': generalInfo.info.get('forwardEps', 'N/A'),
        'AvgVolume': generalInfo.info.get('averageVolume', 'N/A'),
        'Volume': generalInfo.info.get('volume', 'N/A'),
        'Bid': generalInfo.info.get('bid', 'N/A'),
        'Ask': generalInfo.info.get('ask', 'N/A'),
        'Open': generalInfo.info.get('open', 'N/A'),
        'EBITDA': generalInfo.info.get('ebitda', 'N/A'),
        'Float': generalInfo.info.get('floatShares', 'N/A'),
        'SharesShort': generalInfo.info.get('sharesShort', 'N/A'),
        'ShortRatio': generalInfo.info.get('shortRatio', 'N/A'),
        'ShortPercOfFloat': generalInfo.info.get('shortPercentOfFloat', 'N/A'),
        'Revenue': generalInfo.info.get('totalRevenue', 'N/A'),
        'NetIncome': generalInfo.info.get('netIncomeToCommon', 'N/A'),
        'ProfitMargin': generalInfo.info.get('profitMargins', 'N/A'),
        'LastFiscalYearEnd': generalInfo.info.get('lastFiscalYearEnd', 'N/A'),
        'NextFiscalYearEnd': generalInfo.info.get('nextFiscalYearEnd', 'N/A'),
        'MarketCap': generalInfo.info.get('marketCap', 'N/A'),
        '52WeekLow': generalInfo.info.get('fiftyTwoWeekLow', 'N/A'),
        '52WeekHigh': generalInfo.info.get('fiftyTwoWeekHigh', 'N/A'),
        '52WeekChange': generalInfo.info.get('52WeekChange', 'N/A'),
        'DayLow': generalInfo.info.get('dayLow', 'N/A'),
        'DayHigh': generalInfo.info.get('dayHigh', 'N/A')
    }
    return info

if __name__ == '__main__':
    app.run(debug=True)
