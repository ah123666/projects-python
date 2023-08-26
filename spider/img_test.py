import requests
from bs4 import BeautifulSoup
import urllib.parse

def baidu_image_crawler(keyword, num_images):
    search_url = 'https://image.baidu.com/search/index?tn=baiduimage&word=' + urllib.parse.quote(keyword)

    # 发送搜索请求并获取网页内容
    response = requests.get(search_url)
    print(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取图片URL
    image_tags = soup.find_all('img', class_='main_img')
    count = 0

    for img in image_tags:
        if count == num_images:
            break
        img_url = img.get('data-imgurl')
        print(img_url)
        count += 1

# 调用示例：
keyword = 'cat'  # 要搜索的关键词
num_images = 10  # 要爬取的图片数量
baidu_image_crawler(keyword, num_images)
