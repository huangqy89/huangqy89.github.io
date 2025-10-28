#!/usr/bin/env python3
"""
Google Scholar spider - Python version
Scrapes publications from Google Scholar and generates markdown files
"""

import asyncio
import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

import aiohttp
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 浏览器请求头，模拟真实浏览器
BROWSER_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Cookie': 'NID=514=DCce29Z9EXYVjAV_gfv5v8mr2LSkt8TpJSJyjekWANrLdSbgA3sPNoQp90E7r56NzaYvf95-bCRHdseMX6IgN2FBjaaQswK_vj0DUwshLC7YEATgEVleNHgNHRGAiHbFZsVwJ0Re_B8sjKja0_MqegRBbN2_t-tJEbukPZWfHFg'
}

@dataclass
class Article:
    """文章数据结构"""
    link: str
    title: str
    date: str
    author: str
    venue: str
    excerpt: str
    citation: str
    pdf_url: Optional[str]
    slides_url: str

def clean_text(text: str) -> str:
    """
    清理文本，处理编码问题和特殊字符
    """
    if not text:
        return ""
    
    # 移除替换字符 (�)
    text = re.sub(r'[\uFFFD]', '', text)
    # 移除控制字符
    text = re.sub(r'[\u0000-\u001F\u007F-\u009F]', '', text)
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 去除首尾空白
    text = text.strip()
    
    return text

async def fetch_page(session: aiohttp.ClientSession, url: str) -> str:
    """
    异步获取页面内容
    """
    try:
        async with session.get(url, headers=BROWSER_HEADERS) as response:
            response.raise_for_status()
            content = await response.text(encoding='utf-8')
            return content
    except Exception as e:
        logger.error(f"获取页面失败 {url}: {e}")
        return ""

async def scrape_article_detail(session: aiohttp.ClientSession, link: str) -> Dict[str, str]:
    """
    爬取文章详细信息
    """
    detail_html = await fetch_page(session, link)
    if not detail_html:
        return {"excerpt": "", "date": "", "pdf_url": ""}
    
    soup = BeautifulSoup(detail_html, 'html.parser')
    
    # 提取摘要
    excerpt_elem = soup.select_one('#gsc_oci_descr')
    excerpt = clean_text(excerpt_elem.get_text() if excerpt_elem else "")
    
    # 提取日期
    date_elem = soup.select('.gsc_oci_value')
    date = date_elem[1].get_text() if len(date_elem) > 1 else ""
    
    # 提取PDF链接
    pdf_elem = soup.select_one('#gsc_oci_title_gg a')
    pdf_url = pdf_elem.get('href') if pdf_elem else ""
    
    return {
        "excerpt": excerpt,
        "date": date,
        "pdf_url": pdf_url
    }

async def scrape_scholar_page(scholar_id: str) -> List[Article]:
    """
    爬取Google Scholar页面获取所有文章
    """
    url = f"https://scholar.google.com.hk/citations?user={scholar_id}&hl=zh-CN&pagesize=80"
    
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30),
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        # 获取主页面
        html = await fetch_page(session, url)
        if not html:
            logger.error("无法获取Google Scholar主页")
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('.gsc_a_tr')
        
        if not items:
            logger.warning("未找到任何文章")
            return []
        
        articles = []
        logger.info(f"找到 {len(items)} 篇文章，开始爬取详细信息...")
        
        # 并发爬取文章详细信息
        tasks = []
        for item in items:
            # 提取基本信息
            link_elem = item.select_one('a[href]')
            if not link_elem:
                continue
                
            link = "https://scholar.google.com.hk" + link_elem.get('href')
            title = clean_text(link_elem.get_text())
            
            # 提取作者和期刊信息
            gray_divs = item.select('td.gsc_a_t div.gs_gray')
            author = clean_text(gray_divs[0].get_text()) if len(gray_divs) > 0 else ""
            venue = clean_text(gray_divs[-1].get_text()) if len(gray_divs) > 0 else ""
            
            # 创建异步任务获取详细信息
            task = scrape_article_detail(session, link)
            tasks.append((task, {
                'link': link,
                'title': title,
                'author': author,
                'venue': venue
            }))
        
        # 等待所有任务完成
        for task, basic_info in tasks:
            try:
                detail_info = await task
                
                article = Article(
                    link=basic_info['link'],
                    title=basic_info['title'],
                    date=detail_info['date'],
                    author=basic_info['author'],
                    venue=basic_info['venue'],
                    excerpt=detail_info['excerpt'],
                    citation="",
                    pdf_url=detail_info['pdf_url'],
                    slides_url=""
                )
                articles.append(article)
                logger.info(f"已爬取: {article.title[:50]}...")
                
            except Exception as e:
                logger.error(f"处理文章时出错: {e}")
                continue
    
    return articles

def format_date(date_str: str) -> str:
    """
    格式化日期从 yyyy/mm/dd 到 yyyy-mm-dd
    """
    if not date_str:
        return "2000-01-01"  # 默认日期
    
    # 分割日期部分
    parts = date_str.split('/')
    
    # 补齐位数
    formatted_parts = []
    for part in parts:
        formatted_parts.append(part.zfill(2) if len(part) == 1 else part)
    
    # 根据部分数量补齐完整日期
    if len(formatted_parts) == 1:
        return f"{formatted_parts[0]}-01-01"
    elif len(formatted_parts) == 2:
        return f"{formatted_parts[0]}-{formatted_parts[1]}-01"
    elif len(formatted_parts) >= 3:
        return f"{formatted_parts[0]}-{formatted_parts[1]}-{formatted_parts[2]}"
    else:
        return "2000-01-01"

def create_markdown_template(article: Article) -> str:
    """
    创建Markdown模板
    """
    paperurl_line = f'paperurl: "{article.pdf_url}"' if article.pdf_url else 'paperurl:'
    
    return f'''---
title: "{article.title}"
collection: publications
permalink: "/publication/{article.date}"
excerpt: "{article.excerpt}"
date: "{article.date}"
venue: "{article.venue}"
{paperurl_line}
author: "{article.author}"
poster:
remark:
---'''

async def main(scholar_id: str = "AZAiLpkAAAAJ"):
    """
    主函数：爬取Google Scholar数据
    """
    logger.info(f"开始爬取Google Scholar ID: {scholar_id}")
    
    # 爬取文章数据
    articles = await scrape_scholar_page(scholar_id)
    
    if not articles:
        logger.error("没有爬取到任何文章")
        return
    
    logger.info(f"成功爬取 {len(articles)} 篇文章")
    
    # 输出文章摘要到控制台
    for article in articles:
        if article.excerpt:
            logger.info(f"摘要: {article.excerpt[:100]}...")
    
    # 保存到JSON文件
    script_dir = Path(__file__).parent
    json_file = script_dir / "articles.json"
    
    # 转换为字典格式以便JSON序列化
    articles_data = [asdict(article) for article in articles]
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"文章数据已保存到: {json_file}")

def make_md_files():
    """
    从JSON文件读取数据并生成Markdown文件
    """
    script_dir = Path(__file__).parent
    json_file = script_dir / "articles.json"
    
    if not json_file.exists():
        logger.error(f"JSON文件不存在: {json_file}")
        return
    
    # 读取JSON数据
    with open(json_file, 'r', encoding='utf-8') as f:
        articles_data = json.load(f)
    
    publications_dir = script_dir.parent / "_publications"
    publications_dir.mkdir(exist_ok=True)
    
    logger.info(f"开始生成 {len(articles_data)} 个Markdown文件...")
    
    for article_data in articles_data:
        # 创建Article对象
        article = Article(**article_data)
        
        # 格式化日期
        article.date = format_date(article.date)
        
        # 生成Markdown内容
        content = create_markdown_template(article)
        
        # 生成文件名
        filename = f"{article.date.replace('/', '-')}.md"
        filepath = publications_dir / filename
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"生成文件: {filepath}")
    
    logger.info("所有Markdown文件生成完成!")

if __name__ == "__main__":
    # 取消注释下面的行来运行爬虫
    # asyncio.run(main("AZAiLpkAAAAJ"))
    
    # 取消注释下面的行来生成Markdown文件
    make_md_files()