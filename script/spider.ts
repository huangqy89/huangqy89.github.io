//!#deno run --allow-all script/spider.ts
import { cheerio } from "cheerio"
import Logger from "logger"

const kBrowserID = {
    Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Cookie": `NID=514=DCce29Z9EXYVjAV_gfv5v8mr2LSkt8TpJSJyjekWANrLdSbgA3sPNoQp90E7r56NzaYvf95-bCRHdseMX6IgN2FBjaaQswK_vj0DUwshLC7YEATgEVleNHgNHRGAiHbFZsVwJ0Re_B8sjKja0_MqegRBbN2_t-tJEbukPZWfHFg`
}

interface Article {
    link: string,
    title: string,
    date: string,
    author: string,
    venue: string,
    excerpt: string,
    citation: string,
    pdfUrl: string,
    slidesUrl: string
}

const logger = new Logger()

// scrape scholar page
async function main(id: string) {
    // read from file
    // const html = await Deno.readTextFile("script/scholar.html")
    const response = await fetch(`https://scholar.google.com.hk/citations?user=${id}&hl=zh-CN`)
    const html = await response.text()
    const $ = cheerio.load(html)
    const items = $(".gsc_a_tr")
    const articles = await Promise.all([...items].map(async item => {
        const element = $(item)
        const link = "https://scholar.google.com.hk" + element.find('a[href]').attr('href');
        const title = element.find('a[href]').text()
        const author = element.find('td.gsc_a_t div.gs_gray').text();
        const venue = element.find('td.gsc_a_t div.gs_gray:last-child').text();
        const response = await fetch(link, {
            headers: {
                ...kBrowserID
            }
        })
        const html = await response.text()
        const detail = cheerio.load(html)
        const excerpt = detail('#gsc_oci_descr').text();
        const date = detail('.gsc_oci_value:eq(1)').text()
        const citation = "";
        const pdfUrl = detail('#gsc_oci_title_gg a').attr('href');
        const slidesUrl = ""
        return {
            link,
            title,
            date,
            author,
            venue,
            excerpt,
            citation,
            pdfUrl,
            slidesUrl
        }
    }))
    for (const article of articles) {
        logger.info(article.excerpt)
    }
    // write to file
    Deno.writeTextFile("script/articles.json", JSON.stringify(articles))
}

const template = (article: Article) => `---
title: "${article.title}"
collection: publications
permalink: "/publication/${article.date}"
excerpt: "${article.excerpt}"
date: "${article.date}"
venue: "${article.venue}"
paperurl: ${article.pdfUrl ? `"${article.pdfUrl}"` : ""}
author: "${article.author}"
poster:
remark:
---`

async function makeMDFile() {
    // read articles from file
    const json = await Deno.readTextFile("script/articles.json");
    const articles: Article[] = JSON.parse(json)
    // write to file
    articles.map(article => {
        //format data from yyyy/mm/dd to yyyy-mm-dd
        const dateParts = article.date.split("/")
        article.date = dateParts.map(part => part.length === 1 ? "0" + part : part).join("-")
        if (dateParts.length == 1) {
            article.date += "-01-01";
        } else if (dateParts.length == 2) {
            article.date += "-01";
        }
        const content = template(article)
        // write to file
        const name = article.date.replace(/\//g, "-")
        const path = `_publications/${name}.md`
        Deno.writeTextFileSync(path, content, { create: true, append: false})
    })
}

// main("AZAiLpkAAAAJ")
makeMDFile()