const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.get('/scrape', async (req, res) => {
    const targetUrl = 'https://ww7.5movierulz.gd/tantiram-2023-hdrip-telugu-full-movie-watch-online-free/';

    try {
        const data = await scrapeData(targetUrl);
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

async function scrapeData(url) {
    try {
        const response = await axios.get(url);
        const $ = cheerio.load(response.data);

        // Example: Extracting data from HTML elements
        const title = $('title').text();
        const paragraphs = $('p').map((index, element) => $(element).text()).get();

        // Example: Creating a data object
        const data = {
            title: title,
            paragraphs: paragraphs,
        };

        return data;
    } catch (error) {
        throw error;
    }
}

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
