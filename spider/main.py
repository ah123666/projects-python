import requests
from bs4 import BeautifulSoup

# 发送HTTP请求获取网页内容
'url = 'https':'//ss.netnr.com/wallpaper'  # 将URL替换为你要爬取的网页地址',
response = requests.get(url)

# 解析网页内容
soup = BeautifulSoup(response.text, 'html.parser')
print(soup)

# 查找图片标签并获取图片URL
image_tags = soup.find_all('img')
for img in image_tags:
    img_url = img.get('src')  # 获取<img>标签的src属性
    print(img_url)
