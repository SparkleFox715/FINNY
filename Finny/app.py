from flask import Flask, render_template, request, jsonify
import requests
import yfinance as yahFin
import time
import json
import os

app = Flask(__name__)

SEC_API_URL = "https://data.sec.gov"
SEC_EMAIL = "pyz4577@gmail.com"
LOCAL_TICKERS_FILE = os.path.join('data', 'company_tickers.json')  # Ensure this file exists locally

def load_company_tickers():
    try:
        with open(LOCAL_TICKERS_FILE, 'r') as file:
            company_tickers = json.load(file)
        return company_tickers
    except Exception as e:
        print(f"Error loading company tickers: {e}")
        return None

def fetch_data_with_retries(url, headers, retries=3, delay=2):
    session = requests.Session()
    session.headers.update(headers)
    
    for attempt in range(retries):
        try:
            print(f"Fetching data from URL: {url}")
            response = session.get(url)
            print(f"Response status code: {response.status_code}")
            response.raise_for_status()
            if response.headers.get('Content-Type', '').startswith('application/json'):
                return response.json()
            else:
                print(f"Response content: {response.text}")
                return response.text
        except requests.exceptions.ConnectionError as e:
            print(f"Attempt {attempt + 1}: Connection error: {e}")
            time.sleep(delay)
        except requests.exceptions.HTTPError as e:
            print(f"Attempt {attempt + 1}: HTTP error: {e.response.status_code}")
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}: Request exception: {e}")
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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'application/json, text/plain, */*',
        'From': SEC_EMAIL,
        'Connection': 'keep-alive'
    }

    # Attempt to fetch CIK lookup from SEC website
    cik_lookup_url = "https://www.sec.gov/files/company_tickers.json"
    print(f"CIK Lookup URL: {cik_lookup_url}")
    cik_lookup_response = fetch_data_with_retries(cik_lookup_url, headers)
    
    # Fallback to local file if fetching fails
    if cik_lookup_response is None:
        print(f"Fetching from local file: {LOCAL_TICKERS_FILE}")
        cik_lookup_response = load_company_tickers()
        if cik_lookup_response is None:
            return jsonify({'error': 'Failed to fetch CIK lookup data and local file not found.'}), 500

    # Debugging output to inspect the response content
    print(f"CIK lookup response type: {type(cik_lookup_response)}")
    print(f"CIK lookup response content: {cik_lookup_response}")

    # Ensure the response is parsed as JSON
    if isinstance(cik_lookup_response, str):
        try:
            cik_lookup_response = json.loads(cik_lookup_response)
        except json.JSONDecodeError:
            return jsonify({'error': 'Failed to parse CIK lookup response as JSON.'}), 500

    # Process the CIK lookup data
    ticker_to_cik = {v['ticker']: v['cik_str'] for v in cik_lookup_response.values()}
    cik = ticker_to_cik.get(ticker)
    if cik is None:
        return jsonify({'error': 'Failed to find CIK for the given ticker.'}), 404

    print(f"Found CIK for {ticker}: {cik}")

    edgar_url = f'https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json'  # Ensure CIK is zero-padded to 10 digits
    print(f"EDGAR URL: {edgar_url}")
    response = fetch_data_with_retries(edgar_url, headers)
    if response is None:
        return jsonify({'error': 'Failed to fetch data from SEC EDGAR API.'}), 500

    filings = response.get('filings', {}).get('recent', {})
    result = []
    for i in range(len(filings.get('accessionNumber', []))):
        filing = {
            'date': filings.get('filingDate', [])[i],
            'type': filings.get('form', [])[i],
            'link': f"https://www.sec.gov/Archives/edgar/data/{cik}/{filings.get('accessionNumber', [])[i].replace('-', '')}/{filings.get('primaryDocument', [])[i]}"
        }
        result.append(filing)

    return jsonify({'filings': result})

@app.route('/fetch-filing-data', methods=['POST'])
def fetch_filing_data():
    filing_url = request.json['filing_url']
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(filing_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        return jsonify({'error': f'Connection error: {e}'}), 500
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'HTTP error: {e.response.status_code}'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Request exception: {e}'}), 500

    return jsonify({'summary': response.text})

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
        '52WeekHigh': generalInfo.info.get('fiftyTwoWeekHigh', 'N/A')
    }
    return info

if __name__ == '__main__':
    app.run(debug=True)
