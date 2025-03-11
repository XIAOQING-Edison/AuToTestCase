"""
基础爬虫模块
定义爬虫的基本接口和共用功能
"""

class BaseCrawler:
    """
    爬虫基类
    定义所有爬虫必须实现的接口和共用功能
    """
    
    def __init__(self, config=None):
        """
        初始化爬虫
        
        Args:
            config (dict, optional): 爬虫配置，如请求头、认证信息等
        """
        self.config = config or {}
        
    async def fetch(self, url):
        """
        获取文档内容
        
        Args:
            url (str): 文档URL
            
        Returns:
            str: 获取到的原始内容
        """
        raise NotImplementedError("子类必须实现fetch方法")
    
    async def parse(self, content):
        """
        解析文档内容
        
        Args:
            content (str): 原始文档内容
            
        Returns:
            str: 解析后的纯文本需求内容
        """
        raise NotImplementedError("子类必须实现parse方法")
    
    async def crawl(self, source):
        """
        完整的爬取过程
        
        Args:
            source (str): 文档来源（通常是URL）
            
        Returns:
            str: 处理后的需求文本
        """
        content = await self.fetch(source)
        return await self.parse(content)
    
    def _normalize_text(self, text):
        """
        标准化文本，移除多余空白字符
        
        Args:
            text (str): 原始文本
            
        Returns:
            str: 标准化后的文本
        """
        if not text:
            return ""
        # 替换换行符为空格
        text = text.replace('\r\n', ' ').replace('\n', ' ')
        # 处理多余空格
        while '  ' in text:
            text = text.replace('  ', ' ')
        return text.strip() 