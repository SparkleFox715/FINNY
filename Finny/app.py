from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import time
import yfinance as yahFin
from datetime import datetime

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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}

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
        '52WeekHigh': generalInfo.info.get('fiftyTwoWeekHigh', 'N/A'),
        '52WeekChange': generalInfo.info.get('52WeekChange', 'N/A'),
        'DayLow': generalInfo.info.get('dayLow', 'N/A'),
        'DayHigh': generalInfo.info.get('dayHigh', 'N/A')
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




if __name__ == '__main__':
    app.run(debug=True)
    # fetch_yahoo_data('TSLA')