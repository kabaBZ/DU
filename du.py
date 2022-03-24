#!/usr/bin/env python
# coding:utf-8
from unittest import result
import requests
from urllib.request import unquote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from hashlib import md5
import time
from selenium.webdriver import ActionChains
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password =  password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


#1902 验证码类型  官方网站>>价格体系 3.4+版 print 后要加()
#实例化浏览器对象
chrome_options = Options()
# chrome_options.add_argument('--proxy-server=http://101.34.214.152:8001')
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
raw_url = 'https://m.dewu.com/router/order/SoldListPage?spuId=8708&productImage=https%3A%2F%2Fcdn.poizon.com%2Fpro-img%2Forigin-img%2F20220212%2F9962f911df4349fd9934b1dd8af932df.jpg&productName=Vans%20Old%20Skool%20Black%20%E7%BB%8F%E5%85%B8%E6%AC%BE%E4%BD%8E%E5%B8%AE%E4%BC%91%E9%97%B2%E6%9D%BF%E9%9E%8B%20%E7%94%B7%E5%A5%B3%E5%90%8C%E6%AC%BE%20%E9%BB%91%E7%99%BD&productPrice=34900&total=86%E4%B8%87%20'
url = unquote(raw_url)
print(url)
driver1 = webdriver.Chrome(chrome_options=chrome_options)
driver1.get(url)
# #30秒内每0.5s检测是否出现元素
# WebDriverWait(driver1, 10).until(EC.presence_of_element_located(
#         (By.XPATH, '//*[@id="dw-slide"]/div')))
#报错截图
time.sleep(10)
driver1.save_screenshot('./aa.png')

def isElementExist_byxpath(driver, element):
    flag = True
    try:
        driver.find_element_by_xpath(element)
        return flag

    except:
        flag = False
        return flag
if isElementExist_byxpath(driver1,'//*[@id="dw-slide"]/div'):
    # 确定验证码对应的坐标，准备进行裁剪
    code_img_ele = driver1.find_element_by_xpath('//*[@id="dw-slide"]/div')
    location = code_img_ele.location
    print(location)
    size = code_img_ele.size
    #坐标求出
    rangle = (int(location['x']),int(location['y']),int(location['x'] + size['width']),int(location['y'] + size['height']))
    #裁剪
    i = Image.open('./aa.png')
    code_img_name = './code.png'
    frame = i.crop(rangle)
    frame.save(code_img_name)
    #提交超级鹰识别,返回四个坐标
    chaojiying = Chaojiying_Client('kabaBZ', 'kaba5643', '930440')	#用户中心>>软件ID 生成一个替换 96001
    im = open('code.png', 'rb').read()													#本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
    print(chaojiying.PostPic(im, 9104)['pic_str'])
    result = chaojiying.PostPic(im, 9104)['pic_str']
    #处理坐标
    all_list = [] #存储即将被点击的点的坐标
    if '|' in result:
        list_1 = result.split('|')
        count_1 = len(list_1)
        for i in range(count_1):
            xy_list = []
            x = int(list_1[i].split(',')[0])
            y = int(list_1[i].split(',')[1])
            xy_list.append(x)
            xy_list.append(y)
            all_list.append(xy_list)
    else:
        xy_list = []
        x = int(result.split(',')[0])
        y = int(result.split(',')[1])
        xy_list.append(x)
        xy_list.append(y)
        all_list.append(xy_list)
    print(all_list)

    #实现点击

    for l in all_list:
        x = l[0]
        y = l[1]
        ActionChains(driver1).move_to_element_with_offset(code_img_ele,x,y).click().perform()
        time.sleep(0.5)
    time.sleep(5)
    a = 1
    while a < 31:
        name = driver1.find_element_by_xpath('/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-view[%d]/uni-view[1]/uni-view[1]'%a).text
        num = driver1.find_element_by_xpath('/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-view[%d]/uni-view[2]'%a).text
        price = driver1.find_element_by_xpath('/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-view[%d]//uni-label'%a).text
        time = driver1.find_element_by_xpath('/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-view[%d]/uni-view[4]'%a).text
        print(name, num, price, time)
        a = a + 1
else:
    a = 1
    while a <31:
        name = driver1.find_element_by_xpath('/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-view[%d]/uni-view[1]/uni-view[1]'%a).text
        num = driver1.find_element_by_xpath('/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-view[%d]/uni-view[2]'%a).text
        price = driver1.find_element_by_xpath('/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-view[%d]//uni-label'%a).text
        time = driver1.find_element_by_xpath('/html/body/uni-app/uni-page/uni-page-wrapper/uni-page-body/uni-view/uni-view[2]/uni-view[%d]/uni-view[4]'%a).text
        print(name, num, price, time)
        a = a + 1
driver1.quit()
