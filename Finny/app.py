import os
import json
import time
import requests
import yfinance as yahFin
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

SEC_API_URL = "https://data.sec.gov"
SEC_EMAIL = "pyz4577@gmail.com"
LOCAL_TICKERS_FILE = os.path.join('data', 'company_tickers.json')

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

    cik_lookup_url = "https://www.sec.gov/files/company_tickers.json"
    print(f"CIK Lookup URL: {cik_lookup_url}")
    cik_lookup_response = fetch_data_with_retries(cik_lookup_url, headers)
    
    if cik_lookup_response is None:
        print(f"Fetching from local file: {LOCAL_TICKERS_FILE}")
        cik_lookup_response = load_company_tickers()
        if cik_lookup_response is None:
            return jsonify({'error': 'Failed to fetch CIK lookup data and local file not found.'}), 500

    print(f"CIK lookup response type: {type(cik_lookup_response)}")
    print(f"CIK lookup response content: {cik_lookup_response}")

    if isinstance(cik_lookup_response, str):
        try:
            cik_lookup_response = json.loads(cik_lookup_response)
        except json.JSONDecodeError:
            return jsonify({'error': 'Failed to parse CIK lookup response as JSON.'}), 500

    ticker_to_cik = {v['ticker']: v['cik_str'] for v in cik_lookup_response.values()}
    cik = ticker_to_cik.get(ticker)
    if cik is None:
        return jsonify({'error': 'Failed to find CIK for the given ticker.'}), 404

    print(f"Found CIK for {ticker}: {cik}")

    edgar_url = f'https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json'
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
    
    
def TimeFormat(timestamps):
    temp = list(timestamps.keys())
    newKeys =[]
    newDict = {}
    for i in range(len(temp)):
        newKeys.append(temp[i].strftime('%Y-%m-%d %X'))
        newDict[newKeys[i]] = timestamps[temp[i]]
    return newDict
    
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
    #going to  include stock information for 1 week, 1 month, 3 months, 6 months, and 1 year
    W1_data  =  yahFin.download(symbol,  period='5d')
    M1_data = yahFin.download(symbol, period='1mo')
    M3_data = yahFin.download(symbol, period='3mo')
    M6_data = yahFin.download(symbol, period='6mo')
    Y1_data = yahFin.download(symbol, period='1y')
    #W1 data
    global W1_open
    W1_open = W1_data['Open'].to_dict()
    W1_open =TimeFormat(W1_open)
    
    W1_high = W1_data['High'].to_dict()
    W1_high =TimeFormat(W1_high)
    
    W1_low = W1_data['Low'].to_dict()
    W1_low =TimeFormat(W1_low)
    
    W1_closing = W1_data['Close'].to_dict()
    W1_closing =TimeFormat(W1_closing)
    
    #M1 data
    M1_open = M1_data['Open'].to_dict()
    M1_open =TimeFormat(M1_open)
    
    M1_high = M1_data['High'].to_dict()
    M1_high =TimeFormat(M1_high)

    M1_low = M1_data['Low'].to_dict()
    M1_low =TimeFormat(M1_low)
    
    M1_closing = M1_data['Close'].to_dict()
    M1_closing =TimeFormat(M1_closing)
    
    #M3 data
    M3_open = M3_data['Open'].to_dict()
    M3_open =TimeFormat(M3_open)
    
    M3_high = M3_data['High'].to_dict()
    M3_high =TimeFormat(M3_high)

    M3_low = M3_data['Low'].to_dict()
    M3_low =TimeFormat(M3_low)
    
    M3_closing = M3_data['Close'].to_dict()
    M3_closing =TimeFormat(M3_closing)
    
    #M6 data
    M6_open = M6_data['Open'].to_dict()
    M6_open =TimeFormat(M6_open)
    
    M6_high = M6_data['High'].to_dict()
    M6_high =TimeFormat(M6_high)
    
    M6_low = M6_data['Low'].to_dict()
    M6_low =TimeFormat(M6_low)
    
    M6_closing = M6_data['Close'].to_dict()
    M6_closing =TimeFormat(M6_closing)
    
    #Y1 data
    Y1_open = Y1_data['Open'].to_dict()
    Y1_open =TimeFormat(Y1_open)
    
    Y1_high = Y1_data['High'].to_dict()
    Y1_high =TimeFormat(Y1_high)
    
    Y1_low = Y1_data['Low'].to_dict()
    Y1_low =TimeFormat(Y1_low)

    Y1_closing = Y1_data['Close'].to_dict() 
    Y1_closing =TimeFormat(Y1_closing)  
    
    # print(W1_open)
    
    # print(D1_data)
    # print(Y1_open)
    # return info, W1_open
    return info, W1_open, W1_low, W1_high, W1_closing, M1_open, M1_low, M1_high, M1_closing, M3_open, M3_low, M3_high, M3_closing, M6_open, M6_low, M6_high, M6_closing, Y1_open, Y1_low, Y1_high, Y1_closing




@app.route('/ai-report')
def ai_report():
    return render_template('aiReport.html')

@app.route('/generate-ai-report', methods=['POST'])
def generate_ai_report():
    selected_options = request.json
    ticker = "AAPL"  # Example: Replace with actual logic to get ticker
    data = fetch_yahoo_data(ticker)
    report_data = {key: value for key, value in data.items() if selected_options.get(key.lower(), False)}
    return jsonify(report_data)

if __name__ == '__main__':
    app.run(debug=True)
    # fetch_yahoo_data('TSLA')