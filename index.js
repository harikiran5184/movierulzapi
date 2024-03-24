const express = require('express');
const request = require('request');
const cheerio = require('cheerio');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

function scrapeLink(url) {
    return new Promise((resolve, reject) => {
        request(url, (error, response, html) => {
            if (!error) {
                const $ = cheerio.load(html);
                const link = $('.main-button.dlbutton').attr('href');
                resolve(link);
            } else {
                reject(error);
            }
        });
    });
}

function getPage(url) {
    return new Promise((resolve, reject) => {
        request(url, (error, response, html) => {
            if (!error) {
                const $ = cheerio.load(html);
                const divs = $('.boxed');
                const data = [];

                for (let i = 2; i < divs.length; i++) {
                    const title = $(divs[i]).find('a');
                    const img = $(divs[i]).find('img');
                    const dat = { title: title.attr('title'), image: img.attr('src'), link: title.attr('href') };
                    data.push(dat);
                }

                resolve(data);
            } else {
                reject(error);
            }
        });
    });
}

app.get('/search', async (req, res) => {
    const query = req.query.query;
    const url = `https://7movierulz.rest/search_movies?s=${query}`;

    try {
        const data = await getPage(url);
        const total = data.length;
        const mainData = { status: true, totalFound: total, url, data };
        res.json(mainData);
    } catch (error) {
        const mainData = { status: false, msg: 'No Data Found' };
        res.json(mainData);
    }
});

app.get('/:language/:page', async (req, res) => {
    const { language, page } = req.params;
    const pageNumber = page*16 || 0;
    let url;

    switch (language) {
        case 'telugu':
            url = `https://7movierulz.rest/category/telugu-featured/page/${pageNumber}`;
            break;
        case 'hindi':
            url = `https://www.5movierulz.blog/category/bollywood-movie-free/page/${pageNumber}`;
            break;
        case 'tamil':
            url = `https://www.5movierulz.blog/category/tamil-movie-free/page/${pageNumber}`;
            break;
        case 'malayalam':
            url = `https://www.5movierulz.blog/category/malayalam-movie-online/page/${pageNumber}`;
            break;
        case 'english':
            url = `https://www.5movierulz.blog/category/category/hollywood-movie-2023/page/${pageNumber}`;
            break;
        default:
            url = null;
    }


    if (url) {
        try {
            const data = await getPage(url);
            const total = data.length;
            const mainData = { status: true, totalFound: total, url, data };
            res.json(mainData);
        } catch (error) {
            const mainData = { status: false };
            res.json(mainData);
        }
    } else {
        const mainData = { status: false };
        res.json(mainData);
    }
});

app.get('/', async (req, res) => {
    const url = 'https://7movierulz.rest/';
    try {
        const data = await getPage(url);
        const total = data.length;
        const mainData = { status: true, totalFound: total, url, data };
        res.json(mainData);
    } catch (error) {
        const mainData = { status: false };
        console.log(error)
        res.json(mainData);
    }
});

app.get('/get', async (req, res) => {
    const url = req.query.url;
    
    try {
        const data = await getMovie(url);
        res.json(data);
    } catch (error) {
        const data = { status: false, msg: 'Unable to get data' };
        res.json(data);
    }
});

async function getMovie(url) {
    return new Promise((resolve, reject) => {
        request(url, (error, response, html) => {
            if (!error) {
                const $ = cheerio.load(html);
                const title = $('h2.entry-title').text().replace('Full Movie Watch Online Free', '');
                const image = $('img.attachment-post-thumbnail.size-post-thumbnail.wp-post-image').attr('src');
                const description = $('p').eq(4).text();
                const torrents = $('a.mv_button_css');
                const torrent = [];
                const otherLinks = [];

                torrents.each((index, element) => {
                    const link = $(element).attr('href');
                    const size = $(element).find('small').eq(0).text();
                    const quality = $(element).find('small').eq(1).text();
                    const data = { magnet: link, size:0, quality };
                    torrent.push(data);
                });

                $('p').each(async (index, element) => {
                    const strongText = $(element).find('strong').text();
                    if (strongText && strongText.includes('Watch Online –')) {
                        const typ = strongText.split('–')[1].trim();
                        const lin = $(element).find('a').attr('href');
                        try {
                            const lin = await scrapeLink(lin);
                            const data = { type: typ, url: lin };
                            otherLinks.push(data);
                        } catch (error) {
                            const data = { type: typ, url: lin };
                            otherLinks.push(data);
                        }
                    }
                });

                const data = {
                    status: true,
                    url,
                    title,
                    description,
                    image,
                    torrent,
                };

                resolve(data);
            } else {
                reject(error);
            }
        });
    });
}

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
