import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import html2text
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 在Render上使用特定的ChromeDriver路径
    if os.environ.get('RENDER'):
        chrome_driver_path = '/usr/bin/chromedriver'
    else:
        chrome_driver_path = 'chromedriver'  # 本地开发环境
        
    service = Service(chrome_driver_path)
    return webdriver.Chrome(service=service, options=chrome_options)

def scrape_to_markdown(url):
    driver = setup_driver()
    try:
        driver.get(url)
        # 等待页面加载
        time.sleep(5)
        
        # 获取渲染后的页面内容
        page_source = driver.page_source
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 移除不需要的元素
        for script in soup(["script", "style"]):
            script.decompose()
            
        # 转换为Markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        markdown_content = h.handle(str(soup))
        
        return markdown_content
        
    except Exception as e:
        return str(e)
    finally:
        driver.quit()

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
        
    url = data['url']
    markdown_content = scrape_to_markdown(url)
    return jsonify({'markdown': markdown_content})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)