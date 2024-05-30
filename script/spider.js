// @source: https://scholar.google.com.hk/citations?user=AZAiLpkAAAAJ
const items = document.querySelectorAll(".gsc_a_tr")
const articles = [...items].map(item => {
    const link = item.querySelector('a[href]').href;
    const title = item.querySelector('a[href]').innerText
    const date = item.querySelector('td.gsc_a_y').innerText
    const author = item.querySelector('td.gsc_a_t div.gs_gray').innerText
    const venue = item.querySelector('td.gsc_a_t div.gs_gray:last-child').innerText;
    const excerpt = "todo#1";
    const citation = "todo#2";
    const pdfUrl = "todo#3"
    const slidesUrl = "todo#4"
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
})

const csv = articles.reduce((text, article, i) => {
    return text + `${article.date}-00-00\t"${article.title}"\t"${article.venue}"\t"${article.excerpt}"\t"${article.citation}"\t${i}\t${article.link}\t${article.pdfUrl}\n`
}, "")