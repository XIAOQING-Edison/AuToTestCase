"""
网页爬虫模块
专门负责爬取内部网页中的需求文档
"""

import aiohttp
import ssl
from bs4 import BeautifulSoup
import logging
import re
from src.crawlers.base_crawler import BaseCrawler

class WebCrawler(BaseCrawler):
    """
    网页爬虫
    针对内部网页PRD文档的爬取和解析
    """
    
    def __init__(self, config=None):
        """
        初始化网页爬虫
        
        Args:
            config (dict, optional): 配置信息，包括：
                - headers: 请求头
                - auth: 认证信息 (username, password)
                - content_selector: CSS选择器，用于定位内容区域
                - exclude_selectors: 要排除的CSS选择器列表
                - login_url: 登录页面URL
                - login_data: 登录表单数据
                - verify_ssl: 是否验证SSL证书，默认为True
        """
        super().__init__(config)
        self.headers = self.config.get('headers', {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.verify_ssl = self.config.get('verify_ssl', True)
        self.session = None
        
    async def _create_session(self):
        """创建和配置一个新的aiohttp会话"""
        if self.session is None or self.session.closed:
            # 创建SSL上下文
            if not self.verify_ssl:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                self.session = aiohttp.ClientSession(headers=self.headers, connector=aiohttp.TCPConnector(ssl=ssl_context))
            else:
                self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session
    
    async def _login(self):
        """执行网页登录流程"""
        if not self.config.get('login_url') or not self.config.get('login_data'):
            logging.info("跳过登录：未提供登录配置")
            return False
            
        session = await self._create_session()
        try:
            async with session.post(
                self.config['login_url'], 
                data=self.config['login_data'],
                allow_redirects=True
            ) as response:
                if response.status == 200:
                    logging.info("登录成功")
                    return True
                else:
                    logging.error(f"登录失败，状态码: {response.status}")
                    return False
        except Exception as e:
            logging.error(f"登录过程出错: {str(e)}")
            return False
    
    async def fetch(self, url):
        """
        从URL获取页面内容
        
        Args:
            url (str): 页面URL
            
        Returns:
            str: 页面HTML内容
        """
        session = await self._create_session()
        
        # 如果配置了登录信息，先尝试登录
        if self.config.get('login_url'):
            await self._login()
            
        # 处理基本认证
        auth = None
        if self.config.get('auth'):
            auth = aiohttp.BasicAuth(
                login=self.config['auth'][0],
                password=self.config['auth'][1]
            )
        
        try:
            async with session.get(url, auth=auth) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logging.error(f"获取页面失败，状态码: {response.status}")
                    return ""
        except Exception as e:
            logging.error(f"获取页面时出错: {str(e)}")
            return ""
        finally:
            if self.session and not self.session.closed:
                await self.session.close()
                self.session = None
    
    async def parse(self, html_content):
        """
        解析HTML内容，提取需求文档
        
        Args:
            html_content (str): 页面HTML内容
            
        Returns:
            str: 提取的需求文本
        """
        if not html_content:
            return ""
            
        # 使用内置的html.parser代替lxml
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 首先删除所有脚本和样式元素
        for script_or_style in soup(["script", "style", "meta", "link", "svg", "path", "button"]):
            script_or_style.decompose()
        
        # 移除不需要的元素
        exclude_selectors = self.config.get('exclude_selectors', [
            'header', 'footer', 'nav', '.navigation', '.sidebar', 
            'script', 'style', '.advertisement', '.menu', '.breadcrumb',
            '#header', '#footer', '#navigation', '#menu', '.banner', '.ad',
            'iframe', '.cookie-notice', '.popup', '.modal'
        ])
        
        for selector in exclude_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # 提取主要内容
        content_selector = self.config.get('content_selector', 'main, .content, .main-content, article, .article, .document, #content, .text, body')
        main_content = soup.select(content_selector)
        
        if not main_content:
            # 如果没有找到指定的内容区域，尝试使用body
            main_content = [soup.body] if soup.body else []
        
        # 处理内容
        result = []
        for content in main_content:
            # 获取所有文本内容，用空格分隔
            text = content.get_text(separator=' ', strip=True)
            # 清理文本
            text = self._clean_text(text)
            if text:
                result.append(text)
        
        # 如果没有找到有效内容，尝试提取所有可见文本
        if not result:
            text = soup.get_text(separator=' ', strip=True)
            text = self._clean_text(text)
            if text:
                result.append(text)
        
        return '\n\n'.join(result)
    
    def _clean_text(self, text):
        """
        清理提取的文本
        
        Args:
            text (str): 原始文本
            
        Returns:
            str: 清理后的文本
        """
        if not text:
            return ""
            
        # 替换HTML实体
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        
        # 替换连续空白字符为单个空格
        text = re.sub(r'\s+', ' ', text)
        
        # 替换连续多个换行为两个换行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 删除开头和结尾的空白
        text = text.strip()
        
        # 删除过短的行（可能是噪音）
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if len(line) > 5:  # 仅保留长度超过5的行
                lines.append(line)
        
        return '\n'.join(lines)
    
    async def extract_requirements(self, url):
        """
        从URL提取需求文档
        
        Args:
            url (str): 需求文档URL
            
        Returns:
            str: 处理后的需求文本
        """
        return await self.crawl(url) 