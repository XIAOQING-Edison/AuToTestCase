"""
爬虫模块
负责爬取各种来源的需求文档，支持多种来源和格式
"""

from src.crawlers.base_crawler import BaseCrawler
from src.crawlers.web_crawler import WebCrawler

__all__ = ['BaseCrawler', 'WebCrawler'] 