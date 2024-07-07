const express = require('express');
const yahooFinance = require('yahoo-finance2').default;
const app = express();
const port = 3000;

app.use(express.static('public'));

app.get('/api/data/:ticker', async (req, res) => {
    const ticker = req.params.ticker;
    try {
        const quote = await yahooFinance.quoteSummary(ticker, { modules: ['summaryDetail', 'price', 'defaultKeyStatistics'] });
        res.json(quote);
    } catch (error) {
        res.status(500).send({ error: 'Error fetching data' });
    }
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
