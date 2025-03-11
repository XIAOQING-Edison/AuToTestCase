#!/usr/bin/env python3
"""
Playwright爬虫 - 专门用于处理需要JavaScript的现代网站
使用Playwright自动化库获取网页内容
"""

import asyncio
import argparse
import os
import logging
from playwright.async_api import async_playwright

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def extract_content(url, output_file=None, selector=None, timeout=30000, wait_for=None):
    """
    使用Playwright提取网页内容
    
    Args:
        url: 要爬取的URL
        output_file: 输出文件路径
        selector: 内容CSS选择器
        timeout: 超时时间(毫秒)
        wait_for: 等待条件(网络空闲/加载完成/特定选择器出现)
        
    Returns:
        提取的内容
    """
    try:
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            )
            
            # 打开新页面
            page = await context.new_page()
            logger.info(f"正在访问 {url}")
            
            # 导航到URL
            try:
                response = await page.goto(url, timeout=timeout, wait_until="domcontentloaded")
                if not response or response.status >= 400:
                    logger.error(f"页面加载失败: HTTP {response.status if response else 'unknown'}")
                    return None
            except Exception as e:
                logger.error(f"导航到URL时出错: {e}")
                return None
                
            # 等待页面加载完成
            if wait_for == "networkidle":
                try:
                    await page.wait_for_load_state("networkidle", timeout=timeout)
                except Exception as e:
                    logger.warning(f"等待网络空闲超时: {e}")
            elif wait_for and wait_for.startswith("#") or wait_for.startswith("."):
                try:
                    await page.wait_for_selector(wait_for, timeout=timeout)
                except Exception as e:
                    logger.warning(f"等待选择器 {wait_for} 超时: {e}")
            else:
                # 默认等待一段时间让JavaScript执行
                await asyncio.sleep(5)
                
            # 获取页面内容
            content = None
            if selector:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        texts = []
                        for element in elements:
                            text = await element.inner_text()
                            texts.append(text)
                        content = "\n\n".join(texts)
                    else:
                        logger.warning(f"未找到匹配选择器的元素: {selector}")
                        # 尝试提取主要内容
                        content = await extract_main_content(page)
                except Exception as e:
                    logger.error(f"提取内容时出错: {e}")
                    content = await extract_main_content(page)
            else:
                # 尝试提取主要内容
                content = await extract_main_content(page)
                
            # 截图保存 (用于调试)
            screenshot_path = output_file + ".png" if output_file else "screenshot.png"
            await page.screenshot(path=screenshot_path)
            logger.info(f"页面截图已保存到: {screenshot_path}")
            
            # 关闭浏览器
            await browser.close()
            
            # 保存内容
            if content and output_file:
                try:
                    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    logger.info(f"内容已保存到: {output_file}")
                except Exception as e:
                    logger.error(f"保存内容时出错: {e}")
            
            return content
    except Exception as e:
        logger.error(f"爬取过程中出错: {e}")
        return None

async def extract_main_content(page):
    """
    尝试从页面提取主要内容文本
    
    Args:
        page: Playwright页面对象
        
    Returns:
        str: 提取的文本内容
    """
    # 尝试各种常见的内容容器选择器
    content_selectors = [
        "article", "main", "#content", "#main-content", ".content", 
        ".main-content", ".article-content", ".document-content",
        ".editor-content", ".document", ".content-main", ".document-main",
        ".doc-content", ".doc-main"
    ]
    
    for selector in content_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                text = await element.inner_text()
                if text and len(text.strip()) > 100:  # 确保有足够的内容
                    return text
        except Exception:
            continue
    
    # 如果未找到特定容器，尝试提取所有文本内容
    try:
        # 尝试提取所有可见文本
        text = await page.evaluate("""() => {
            function isVisible(elem) {
                return !!(elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length);
            }
            
            const elements = Array.from(document.body.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, div'));
            const visibleElements = elements.filter(el => isVisible(el) && 
                                                     !['script', 'style', 'header', 'footer', 'nav'].includes(el.tagName.toLowerCase()) &&
                                                     !el.closest('header') && !el.closest('footer') && !el.closest('nav'));
            return visibleElements.map(el => el.innerText).filter(text => text.trim().length > 0).join('\\n\\n');
        }""")
        
        if text and len(text.strip()) > 100:
            return text
    except Exception as e:
        logger.error(f"提取可见文本时出错: {e}")
    
    # 最后的方法：从body提取所有文本
    try:
        body = await page.query_selector("body")
        if body:
            return await body.inner_text()
    except Exception as e:
        logger.error(f"从body提取文本时出错: {e}")
    
    # 如果上述方法都失败，返回整个HTML内容
    return await page.content()

async def main():
    parser = argparse.ArgumentParser(description="Playwright网页爬虫 - 支持JavaScript渲染的网站")
    parser.add_argument("url", help="要爬取的URL")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--selector", "-s", help="内容选择器(CSS)")
    parser.add_argument("--timeout", "-t", type=int, default=30000, help="超时时间(毫秒)")
    parser.add_argument("--wait-for", "-w", help="等待条件: networkidle 或 CSS选择器")
    
    args = parser.parse_args()
    
    content = await extract_content(
        args.url,
        output_file=args.output,
        selector=args.selector,
        timeout=args.timeout,
        wait_for=args.wait_for
    )
    
    if content:
        print(f"成功提取内容，长度: {len(content)}")
        # 显示前100个字符预览
        preview_length = min(100, len(content))
        print(f"\n内容预览 (前{preview_length}字符):")
        print("-" * 50)
        print(content[:preview_length])
        print("-" * 50)
    else:
        print("未能提取到内容")

if __name__ == "__main__":
    asyncio.run(main()) 