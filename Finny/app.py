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


# Embedded stock descriptions
STOCK_DESCRIPTIONS = {
    'NVDA': """
Short-Term Analysis:
In the short term, NVIDIA Corporation (NVDA) has demonstrated strong momentum, driven by robust demand for its GPUs, particularly in the gaming, data center, and AI markets. Recent earnings reports have consistently exceeded expectations, with significant revenue growth and expanding margins. The company’s strategic positioning in the AI and machine learning sectors has made it a key player in these rapidly growing markets. However, the stock’s high valuation has led to some volatility, as investors weigh the potential for future growth against current pricing levels.

Intermediate-Term Analysis:
Over the intermediate term, NVIDIA’s growth prospects remain bright, particularly as the company continues to innovate and expand its product offerings. The ongoing shift towards AI-driven applications, cloud computing, and autonomous vehicles presents substantial opportunities for NVDA. The company’s acquisition strategy, such as the attempted purchase of Arm Holdings, reflects its ambition to dominate the semiconductor industry. Regulatory challenges and integration risks are potential hurdles, but successful execution could significantly enhance NVIDIA’s competitive advantage and drive further growth in the intermediate term.

Long-Term Analysis:
In the long term, NVIDIA is well-positioned to benefit from several secular trends, including the proliferation of AI, the rise of edge computing, and the expansion of the metaverse. As the demand for advanced computing power continues to grow, NVDA’s cutting-edge technologies are likely to remain in high demand. The company’s focus on research and development, coupled with strategic partnerships and acquisitions, should help sustain its leadership in the semiconductor industry. However, competition from other tech giants and potential shifts in technology trends could pose challenges, requiring NVIDIA to continually adapt and innovate.

Summary:
NVIDIA Corporation is a leader in the semiconductor industry, with strong short-term performance driven by high demand for its GPUs across multiple sectors. The company’s intermediate-term prospects are promising, supported by its strategic positioning in key growth markets and ongoing innovation. In the long term, NVIDIA’s focus on AI, edge computing, and other emerging technologies should continue to drive growth, though the company will need to navigate competitive pressures and evolving industry dynamics. Overall, NVDA remains a compelling investment, with significant potential for both growth and volatility.
"""
,
    'META': """
Short-Term Analysis:
In the short term, Meta Platforms, Inc. (META) has faced a challenging environment, with increased scrutiny from regulators and ongoing concerns about privacy and data security. Despite these challenges, the company continues to deliver strong financial results, driven by its dominant position in the digital advertising market. Meta's user base across its platforms, including Facebook, Instagram, and WhatsApp, remains robust, providing a steady stream of ad revenue. However, the stock has seen some volatility due to investor concerns about regulatory risks and the company’s heavy investments in the metaverse.

Intermediate-Term Analysis:
Over the intermediate term, Meta’s future will largely depend on its ability to successfully navigate the transition from a social media giant to a leader in the emerging metaverse. The company has committed significant resources to developing virtual and augmented reality technologies, with the goal of creating immersive digital experiences. While this strategic shift presents significant growth opportunities, it also comes with substantial risks, including high capital expenditures and uncertain consumer adoption. Additionally, Meta will need to address ongoing challenges related to content moderation, data privacy, and regulatory pressure to maintain its market position.

Long-Term Analysis:
In the long term, Meta’s success will hinge on its ability to execute its vision for the metaverse and continue expanding its ecosystem of services. The company’s focus on building a new digital frontier could redefine social interaction and commerce, potentially unlocking new revenue streams. However, this ambitious endeavor will require sustained innovation, significant investment, and the ability to overcome technical and regulatory hurdles. While Meta’s core advertising business is expected to remain strong, the long-term outlook will be influenced by how well the company can integrate and monetize its metaverse initiatives, as well as its ability to maintain user trust and engagement.

Summary:
Meta Platforms, Inc. is at a critical juncture, with strong short-term performance supported by its dominant position in digital advertising. The intermediate-term outlook is mixed, with the company making bold bets on the metaverse that could either propel it to new heights or expose it to significant risks. In the long term, Meta's success will depend on its ability to execute its metaverse strategy and adapt to evolving regulatory landscapes. While the company remains a key player in the tech industry, investors should be mindful of the risks associated with its ambitious plans and the changing digital landscape.
"""
,
    'AMD': """
Short-Term Analysis:
In the short term, Advanced Micro Devices, Inc. (AMD) has experienced strong performance, bolstered by continued demand for its Ryzen processors and Radeon graphics cards. The company's latest earnings reports have highlighted impressive revenue growth, driven by gains in both the consumer and data center markets. AMD’s competitive pricing and technological advancements have enabled it to capture market share from rivals like Intel. However, the stock remains sensitive to broader market conditions and investor sentiment, especially given the highly competitive nature of the semiconductor industry.

Intermediate-Term Analysis:
Over the intermediate term, AMD’s prospects are promising as it continues to innovate and expand its product lineup. The company’s focus on high-performance computing, gaming, and data centers positions it well in key growth areas. The successful launch of new products, such as the next generation of Ryzen CPUs and EPYC processors, is expected to drive further revenue growth and profitability. Partnerships with major tech companies and increasing penetration in the server market should also support sustained growth. However, maintaining this momentum will require AMD to continue executing effectively against strong competition.

Long-Term Analysis:
In the long term, AMD is well-positioned to benefit from trends such as the ongoing demand for high-performance computing, the growth of cloud services, and the rise of AI and machine learning applications. The company’s commitment to innovation and its ability to adapt to changing market conditions will be critical to its success. While competition from both established players and new entrants will remain a challenge, AMD’s strong brand, technological edge, and strategic partnerships provide a solid foundation for long-term growth. Additionally, the company's efforts to diversify its revenue streams should help mitigate risks associated with market fluctuations.

Summary:
Advanced Micro Devices, Inc. has demonstrated strong short-term performance, driven by demand for its innovative processors and graphics cards. The intermediate-term outlook is positive, with continued growth expected from new product launches and market share gains. In the long term, AMD is well-positioned to capitalize on key industry trends, though it will need to navigate a highly competitive landscape. Overall, AMD presents a compelling investment opportunity, with significant growth potential balanced by the inherent risks of the semiconductor industry.
"""
,
    'GOOG': """
Short-Term Analysis:
In the short term, Alphabet Inc. (GOOG) has continued to deliver strong financial performance, driven by its dominant position in the digital advertising market through Google Search, YouTube, and its broader advertising network. The company's recent earnings reports have showcased robust revenue growth, particularly in its core advertising business, despite economic uncertainties. Additionally, Alphabet’s cloud computing division, Google Cloud, has been gaining traction, contributing to overall revenue diversification. However, the stock has experienced some volatility due to macroeconomic concerns and regulatory scrutiny, particularly around antitrust issues.

Intermediate-Term Analysis:
Over the intermediate term, Alphabet’s growth prospects remain solid, supported by its continued investments in artificial intelligence (AI), cloud computing, and hardware. Google Cloud is expected to be a significant growth driver as more businesses adopt cloud services, and AI advancements are likely to enhance the company’s existing products and services. Furthermore, Alphabet's focus on expanding its hardware offerings, such as Pixel devices and Google Nest, adds another layer of revenue diversification. However, the company will need to navigate increasing regulatory pressures and competition in the cloud and digital advertising markets to sustain its growth momentum.

Long-Term Analysis:
In the long term, Alphabet is well-positioned to benefit from its leadership in AI and its vast ecosystem of products and services. The company’s commitment to innovation and its ability to integrate AI into its offerings are likely to drive continued growth in areas like search, cloud computing, and autonomous technologies. Alphabet’s Other Bets segment, which includes ventures like Waymo (autonomous vehicles) and Verily (healthcare), has the potential to unlock new growth opportunities if these projects reach commercial viability. However, the company will need to address ongoing regulatory challenges and maintain its competitive edge in the face of evolving technology trends and consumer preferences.

Summary:
Alphabet Inc. remains a powerhouse in the tech industry, with strong short-term performance fueled by its leadership in digital advertising and growing presence in cloud computing. The intermediate-term outlook is positive, driven by continued innovation and expansion into AI, cloud, and hardware. In the long term, Alphabet's success will depend on its ability to capitalize on AI advancements, explore new growth opportunities, and navigate regulatory challenges. While GOOG is considered a strong investment, investors should be mindful of the potential risks associated with increased competition and regulatory scrutiny.
"""
,
    'GME': """
Short-Term Analysis:
In the short term, GameStop Corp. (GME) has seen increased volatility, largely driven by its status as a highly speculative stock within the retail investor community. The stock has experienced sharp price swings due to ongoing interest from retail traders on platforms like Reddit, as well as fluctuations in short interest. The company’s recent quarterly earnings reports have shown a mixed performance, with revenue seeing modest growth, but profitability remaining a challenge. Management has been focusing on cost-cutting measures and reducing debt, which could provide some short-term stability, though the market's reaction to any financial updates is likely to be highly sensitive.

Intermediate-Term Analysis:
Over the intermediate term, GME’s future will largely depend on its ability to successfully pivot from a brick-and-mortar retailer to a more digital-focused business model. The company has made strides in e-commerce, with online sales now constituting a larger portion of its revenue. However, competition in the digital space is fierce, and GME must navigate challenges such as securing exclusive content or partnerships and expanding its customer base beyond its traditional gaming audience. The stock’s performance in this period will likely be influenced by how well the company can execute its turnaround strategy and adapt to the rapidly changing retail environment.

Long-Term Analysis:
In the long term, GameStop’s viability as a company will depend on its ability to diversify and stabilize its revenue streams. The gaming industry is evolving, with a shift towards digital downloads and cloud gaming, which could erode the demand for physical game sales—a traditional stronghold for GME. The company has hinted at exploring new business ventures, such as blockchain technology and NFTs, which could provide new growth avenues if executed correctly. However, the long-term outlook is uncertain, as it hinges on the company’s ability to innovate and stay relevant in an industry that is increasingly dominated by digital and cloud-based solutions.

Summary:
GameStop remains a highly speculative investment, with its stock price driven more by market sentiment and retail investor enthusiasm than by fundamentals. In the short term, volatility is expected to continue, while the intermediate-term outlook depends on the company’s execution of its digital transformation. Long-term prospects are uncertain, with success contingent on GME's ability to innovate and adapt to industry trends. Investors should approach GME with caution, considering both the potential for significant upside if the turnaround is successful and the substantial risks if the company fails to adapt.
"""
,
    'TSLA': """
Short-Term Analysis:
In the short term, Tesla, Inc. (TSLA) has continued to show strong performance, driven by robust demand for its electric vehicles (EVs) across major markets, particularly in North America, Europe, and China. The company's recent earnings reports have highlighted significant revenue growth, fueled by increased vehicle deliveries, expanding production capacity, and strong profit margins. Tesla's ability to navigate supply chain challenges, particularly in securing semiconductor chips, has been a key factor in its short-term success. However, the stock remains highly volatile, influenced by market sentiment, production updates, and broader economic conditions.

Intermediate-Term Analysis:
Over the intermediate term, Tesla’s growth prospects are underpinned by its aggressive expansion plans, including new Gigafactories in key regions, the launch of new models like the Cybertruck and Semi, and the development of advanced battery technologies. The company's focus on scaling production and lowering costs is expected to drive further revenue growth and market share gains in the increasingly competitive EV market. Additionally, Tesla’s foray into energy solutions, such as solar products and energy storage systems, provides another avenue for growth. However, the company will face challenges from both established automakers and new entrants in the EV space, requiring continuous innovation and efficient execution.

Long-Term Analysis:
In the long term, Tesla is poised to benefit from the global shift towards sustainable energy and transportation. The company’s leadership in the EV market, combined with its advancements in autonomous driving technology, positions it well to capitalize on future trends in mobility. Tesla’s vision of creating a fully integrated energy ecosystem—comprising EVs, solar power, and energy storage—could redefine the automotive and energy industries. However, sustaining long-term growth will depend on Tesla’s ability to scale its operations, maintain its technological edge, and navigate potential regulatory and competitive challenges. The success of Tesla's ventures into AI and robotics, such as the Tesla Bot, could also play a critical role in shaping its future.

Summary:
Tesla, Inc. remains a leader in the electric vehicle market, with strong short-term performance driven by increasing demand and expanding production capacity. The intermediate-term outlook is promising, supported by new product launches, scaling of production, and diversification into energy solutions. In the long term, Tesla’s success will be closely tied to its ability to innovate, execute its vision for a sustainable energy future, and maintain its competitive edge in the face of growing industry competition. While TSLA is seen as a high-growth investment, it comes with significant volatility and risks associated with its ambitious goals and evolving market dynamics.
"""
,
    'MSFT': """
Short-Term Analysis:
In the short term, Microsoft Corporation (MSFT) continues to demonstrate strong financial performance, driven by its diverse product portfolio and leadership in key areas such as cloud computing, productivity software, and gaming. Recent earnings reports have highlighted robust revenue growth, particularly from its Azure cloud services, which have seen increasing adoption across various industries. Additionally, Microsoft's Office 365 and Teams platforms have maintained strong user growth, supported by the ongoing shift towards remote and hybrid work. The stock has shown resilience, although it remains sensitive to broader market conditions and macroeconomic factors.

Intermediate-Term Analysis:
Over the intermediate term, Microsoft’s growth prospects are promising, fueled by continued innovation and expansion in cloud computing, artificial intelligence (AI), and enterprise solutions. Azure is expected to remain a key growth driver, as more businesses migrate to the cloud and leverage AI and machine learning capabilities. The company’s acquisition strategy, including the high-profile purchase of Activision Blizzard, positions Microsoft to strengthen its presence in the gaming industry and expand its content offerings. Additionally, Microsoft's investments in AI and automation are likely to enhance its competitive edge across various product lines. However, the company will need to navigate regulatory scrutiny, particularly around its acquisitions and market dominance.

Long-Term Analysis:
In the long term, Microsoft is well-positioned to benefit from several secular trends, including the digital transformation of businesses, the rise of cloud computing, and the growing demand for AI-driven solutions. The company’s focus on integrating AI into its products and services, along with its strong presence in the enterprise software market, should ensure sustained growth. Microsoft’s extensive ecosystem, including Windows, Office, Azure, and its gaming division, provides multiple avenues for revenue generation and customer engagement. As technology continues to evolve, Microsoft’s ability to innovate and adapt will be critical to maintaining its leadership position. The company’s strong financial position, with substantial cash reserves, also allows it to explore new growth opportunities and weather economic uncertainties.

Summary:
Microsoft Corporation remains a dominant force in the technology sector, with strong short-term performance driven by its leadership in cloud computing and productivity software. The intermediate-term outlook is positive, supported by continued innovation, strategic acquisitions, and expansion into new markets. In the long term, Microsoft’s success will depend on its ability to capitalize on digital transformation trends, integrate AI into its offerings, and maintain its competitive edge. While MSFT is considered a relatively stable and growth-oriented investment, investors should be aware of potential risks associated with regulatory challenges and the highly competitive nature of the tech industry.
"""
,
    'INTC': """
Short-Term Analysis:
In the short term, Intel Corporation (INTC) faces a period of transition as it works to address supply chain challenges and competitive pressures in the semiconductor industry. Recent earnings reports have shown mixed results, with some revenue growth driven by strong demand for its data center and PC processors, but also facing challenges related to manufacturing delays and increased competition from AMD and other chipmakers. Intel's efforts to ramp up production and address its process technology issues are crucial for stabilizing its short-term performance. The stock has experienced volatility as investors react to these operational challenges and strategic updates.

Intermediate-Term Analysis:
Over the intermediate term, Intel's prospects are influenced by its strategic initiatives to regain technological leadership and expand its market presence. The company’s focus on improving its process technology, including the transition to 7nm and 5nm nodes, is essential for competing effectively in the high-performance computing and data center markets. Intel's investments in new product lines, such as its upcoming GPUs and advancements in AI and edge computing, are expected to drive future growth. Additionally, partnerships and collaborations aimed at enhancing its product offerings and manufacturing capabilities will play a significant role in its intermediate-term performance. However, maintaining competitive edge amidst growing competition from rivals like AMD and NVIDIA will be a key challenge.

Long-Term Analysis:
In the long term, Intel's success will hinge on its ability to execute its technology roadmap and adapt to evolving industry trends. The company's substantial investments in R&D and its efforts to innovate in areas such as AI, quantum computing, and advanced manufacturing processes will be critical for sustaining growth and market leadership. Intel's strategic focus on expanding its semiconductor manufacturing capabilities and exploring new markets, including automotive and 5G technology, positions it well for future opportunities. However, the semiconductor industry’s rapid evolution and intense competition require continuous innovation and strategic agility. Intel’s ability to maintain technological leadership and effectively compete in a changing market landscape will be essential for long-term success.

Summary:
Intel Corporation is navigating a period of significant transformation, with short-term performance impacted by supply chain issues and competitive pressures. The intermediate-term outlook is shaped by the company's strategic initiatives to improve its technology and expand its market presence. In the long term, Intel’s success will depend on its ability to innovate and adapt to industry trends while maintaining competitive edge. While INTC offers potential for growth, investors should be aware of the challenges associated with the rapidly evolving semiconductor industry and the company’s ongoing efforts to regain market leadership.
"""
,
    'AAPL': """
Short-Term Analysis:
In the short term, Apple Inc. (AAPL) continues to demonstrate strong performance, driven by robust demand for its latest iPhone models, wearables, and services. The company’s recent earnings reports have consistently shown solid revenue growth and strong profitability, supported by its loyal customer base and ecosystem of devices and services. Apple’s ability to navigate supply chain challenges, particularly in the semiconductor space, has also contributed to its resilience. However, the stock remains sensitive to broader market conditions, especially given its significant weight in major indices and the tech sector’s overall performance.

Intermediate-Term Analysis:
Over the intermediate term, Apple’s growth prospects are supported by its continued innovation and expansion into new product categories and services. The company’s focus on enhancing its ecosystem, including services such as Apple Music, iCloud, and Apple TV+, is expected to drive recurring revenue and increase customer retention. Additionally, Apple’s foray into augmented reality (AR) and potential developments in the automotive sector, particularly with the rumored Apple Car, could unlock new revenue streams. However, competition in these emerging markets is intense, and Apple will need to leverage its brand strength and innovation capabilities to maintain its growth trajectory.

Long-Term Analysis:
In the long term, Apple is well-positioned to benefit from its strong brand, loyal customer base, and ability to innovate. The company’s commitment to sustainability and advancements in health-related technologies, such as the Apple Watch’s health monitoring features, are likely to resonate with consumers and drive long-term demand. Additionally, Apple’s substantial cash reserves and strategic investments provide it with the flexibility to explore new growth opportunities and weather economic downturns. However, as the smartphone market matures, Apple will need to continue diversifying its revenue streams and finding new areas for growth to sustain its leadership in the tech industry.

Summary:
Apple Inc. remains a leader in the tech industry, with strong short-term performance driven by demand for its flagship products and services. The intermediate-term outlook is positive, with continued innovation and expansion into new markets expected to support growth. In the long term, Apple’s ability to maintain its brand strength, diversify its revenue streams, and innovate in emerging technologies will be key to its success. While AAPL is considered a relatively stable investment, investors should be aware of the challenges posed by market saturation and increasing competition in new product categories.
"""

}


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
    newDict = {}
    for timestamp, value in timestamps.items():
        formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        newDict[formatted_time] = value
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
    # Stock data for different periods
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
   
    return info, W1_open, W1_low, W1_high, W1_closing, M1_open, M1_low, M1_high, M1_closing, M3_open, M3_low, M3_high, M3_closing, M6_open, M6_low, M6_high, M6_closing, Y1_open, Y1_low, Y1_high, Y1_closing




    data_dict = {}
    for period_key, period_value in periods.items():
        data = yahFin.download(symbol, period=period_value)
        if data.empty:
            continue
        data_dict[f'{period_key}_open'] = TimeFormat(data['Open'].to_dict())
        data_dict[f'{period_key}_high'] = TimeFormat(data['High'].to_dict())
        data_dict[f'{period_key}_low'] = TimeFormat(data['Low'].to_dict())
        data_dict[f'{period_key}_closing'] = TimeFormat(data['Close'].to_dict())
    return {'info': info, 'historical_data': data_dict}


@app.route('/ai-report')
def ai_report():
    return render_template('aiReport.html')


@app.route('/fetch-stock-text', methods=['POST'])
def fetch_stock_text():
    ticker = request.json.get('ticker', '').upper()
    description = STOCK_DESCRIPTIONS.get(ticker, "No description available for this ticker.")
    return jsonify({'text': description})


# Optional: If you want to remove this route since it's redundant
# @app.route('/generate-ai-report', methods=['POST'])
# def generate_ai_report():
#     ticker = request.json.get('ticker', '').upper()
#     description = STOCK_DESCRIPTIONS.get(ticker, "No description available for this ticker.")
#     return jsonify({'description': description})


if __name__ == '__main__':
    app.run(debug=True)



