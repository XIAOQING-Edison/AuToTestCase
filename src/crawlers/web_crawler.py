"""
网页爬虫模块
专门负责爬取内部网页中的需求文档
"""

import aiohttp
import asyncio
import ssl
from bs4 import BeautifulSoup
import logging
import re
import os
import json
from src.crawlers.base_crawler import BaseCrawler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
                - use_selenium: 是否使用Selenium(处理JS渲染的网站)
        """
        super().__init__(config)
        self.headers = self.config.get('headers', {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.verify_ssl = self.config.get('verify_ssl', True)
        self.session = None
        self.driver = None
        self.logged_in = False
        self.logger = logging.getLogger(__name__)
        
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
                    self.logged_in = True
                    return True
                else:
                    logging.error(f"登录失败，状态码: {response.status}")
                    return False
        except Exception as e:
            logging.error(f"登录过程出错: {str(e)}")
            return False
    
    def _setup_selenium(self, no_verify_ssl=False):
        """设置Selenium WebDriver"""
        if self.driver is not None:
            return self.driver
            
        options = Options()
        options.add_argument('--headless')  # 无头模式
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        if no_verify_ssl:
            options.add_argument('--ignore-certificate-errors')
            
        # 添加用户代理
        options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # 添加cookies（如果有）
        cookies = self.config.get('cookies', {})
        
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            return self.driver
        except Exception as e:
            self.logger.error(f"设置Selenium时出错: {e}")
            raise
    
    async def fetch(self, url, no_verify_ssl=False, use_selenium=None):
        """
        获取URL内容
        
        Args:
            url: 要获取的URL
            no_verify_ssl: 是否禁用SSL验证
            use_selenium: 是否使用Selenium（覆盖配置中的设置）
            
        Returns:
            str: HTML内容
        """
        should_use_selenium = use_selenium if use_selenium is not None else self.config.get('use_selenium', False)
        
        if should_use_selenium:
            self.logger.info(f"使用Selenium获取: {url}")
            try:
                driver = self._setup_selenium(no_verify_ssl)
                driver.get(url)
                
                # 等待页面加载（可根据需要调整）
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 如果配置中指定了内容选择器，等待该元素出现
                content_selector = self.config.get('content_selector')
                if content_selector:
                    try:
                        WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, content_selector))
                        )
                    except Exception as e:
                        self.logger.warning(f"等待内容选择器时超时: {e}")
                
                # 获取页面内容
                html_content = driver.page_source
                return html_content
            except Exception as e:
                self.logger.error(f"使用Selenium获取{url}时出错: {e}")
                raise
        else:
            self.logger.info(f"使用aiohttp获取: {url}")
            # 如果需要登录，先执行登录
            if self.config.get('login_url'):
                await self._login()
                
            session = await self._create_session()
            try:
                # 创建SSL上下文
                ssl_context = None
                if no_verify_ssl:
                    ssl_context = ssl._create_unverified_context()
                    
                auth = None
                auth_username = self.config.get('auth_username')
                auth_password = self.config.get('auth_password')
                if auth_username and auth_password:
                    auth = aiohttp.BasicAuth(auth_username, auth_password)
                    
                async with session.get(url, auth=auth, ssl=ssl_context) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        self.logger.error(f"HTTP错误: {response.status}")
                        raise Exception(f"HTTP错误: {response.status}")
            except Exception as e:
                self.logger.error(f"获取{url}时出错: {e}")
                self.logger.error(f"获取页面时出错: {e}")
                raise
    
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
    
    async def extract_requirements(self, url, no_verify_ssl=False, use_selenium=None):
        """
        从URL提取需求文档
        
        Args:
            url (str): 需求文档URL
            no_verify_ssl: 是否禁用SSL验证
            use_selenium: 是否使用Selenium
            
        Returns:
            str: 处理后的需求文本
        """
        try:
            html_content = await self.fetch(url, no_verify_ssl, use_selenium)
            requirements = await self.parse(html_content)
            return requirements
        except Exception as e:
            self.logger.error(f"提取需求时出错: {e}")
            raise
    
    async def close(self):
        """关闭资源"""
        if self.session:
            await self.session.close()
            self.session = None
            
        if self.driver:
            self.driver.quit()
            self.driver = None 