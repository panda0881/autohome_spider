# -*- coding:utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time


# 从爬取的HTML文件中获取相关分类的得分
def get_score(str1, name):
    str1 = str1.strip('\n')
    str1 = str1.strip(name)
    str1 = str1.strip('\n')
    return str1


# 将页面拆解成多个评论
def get_comments_in_page(soup_x, total_list):
    for comment_list in soup_x.find_all("div", class_='mouthcon'):
        comment_detail = get_details_of_comment(comment_list, spider=spider)
        total_list.append(comment_detail)


# 获取用户性别
def get_user_gender(spider2, url):
    spider2.get(url + '/info')
    deal_the_page(spider2)
    soup = BeautifulSoup(spider2.page_source)
    gender = soup.find('div', class_='uData')
    list1 = gender.find_all('p')
    result = ''
    for p in list1:
        if '性别' in p.text:
            result = p.text.replace('\n', '')
    return result


# 将一条评论拆解成多个部分，并存储起来
def get_details_of_comment(comment, spider):
    review = dict()
    find_location = comment.find_all("dl", class_='choose-dl')
    for dl in find_location:
        if "购买地点" in dl.text:
            review['location'] = dl.text.replace('\n', '').replace(' ', '').strip('购买地点')
        if "动力" in dl.text:
            review['score_power'] = get_score(dl.text, '动力')
        if "空间" in dl.text:
            review['score_space'] = get_score(dl.text, '空间')
        if "操控" in dl.text:
            review['score_control'] = get_score(dl.text, '操控')
        if "油耗" in dl.text:
            review['score_consume'] = dl.text.replace('\n', '').replace(' ', '').strip('油耗')
        if "舒适性" in dl.text:
            review['score_comfort'] = get_score(dl.text, '舒适性')
        if "外观" in dl.text:
            review['score_outlook'] = get_score(dl.text, '外观')
        if "内饰" in dl.text:
            review['score_appearance'] = get_score(dl.text, '内饰')
        if "性价比" in dl.text:
            review['score_value'] = get_score(dl.text, '性价比')
        if "购车目的" in dl.text:
            review['purpose'] = dl.text.replace('\n', '').strip('购车目的')
        if "购买车型" in dl.text:
            review['car_size'] = dl.text.replace('\n', '').strip('购买车型')
    review['title and time'] = comment.find("div", class_='title-name name-width-01').text.replace('\n', '').replace(
        ' ', '')
    review['author'] = comment.find("div", class_='name-text').text.replace('\n', '').replace(' ', '')
    review['user_link'] = comment.find("div", class_='name-text').p.a['href']
    review['gender'] = get_user_gender(spider, review['user_link'])
    try:
        review['content'] = comment.find("div", class_='text-con height-list').div.text
    except:
        print('dont have content')
    return review


# 将页面的所有信息显示出来
def deal_the_page(spider1):
    try:
        spider1.find_element_by_xpath('//div[@class="step01"]/a[@class="close"]')
        spider1.find_element_by_xpath('//div[@class="step01"]/a[@class="close"]').click()
        print('fuck the advertise')
    except:
        print('haha no ad')
    click_list = spider1.find_elements_by_xpath(
        "//div[@class='mouthcon']//a[@class='btn btn-small fn-left js-showmessage']")
    for a in click_list:
        a.click()
        time.sleep(0.5)
        print('click')


# 通过一个车的车辆编码，获取相关的所有评论数据
def get_review_data(car_code, spider):
    spider.get('http://k.autohome.com.cn/' + car_code + '/###')
    deal_the_page(spider)
    soup = BeautifulSoup(spider.page_source)
    total_comment_list = list()
    get_comments_in_page(soup, total_comment_list)
    loop_count = 1
    for a in range(2, 11):
        url = 'http://k.autohome.com.cn/' + car_code + '/index_' + str(a) + '.html###'
        time.sleep(10)
        spider.get(url)
        deal_the_page(spider)
        soup1 = BeautifulSoup(spider.page_source)
        get_comments_in_page(soup1, total_comment_list)
        loop_count += 1
    return total_comment_list


# 通过一个车的车辆编码，获取相关的所有论坛评论数据
def get_luntan_data(car_code, spider):
    url_list = list()
    luntan_list = list()
    for a in range(1, 11):
        spider.get('http://club.autohome.com.cn/bbs/forum-c-' + car_code + '-' + str(a) + '.html')
        soup = BeautifulSoup(spider.page_source)
        link_list = soup.find_all('a', class_='a_topic')
        for link in link_list:
            url_list.append('http://club.autohome.com.cn/' + link['href'])
    i = 0
    for url in url_list:
        i += 1
        print(i)
        try:
            review = dict()
            spider.get(url)
            soup = BeautifulSoup(spider.page_source)
            content = soup.find('div', class_='conttxt')
            wanted_list = content.find_all('div', class_='tz-paragraph')
            total_content = ''
            for wenzi in wanted_list:
                if len(wenzi.text.replace('\n', '').replace(' ', '')) > 0:
                    print(wenzi)
                    total_content += wenzi.text.replace('\n', '').replace(' ', '')
                else:
                    print('empty')
            review['website'] = url
            review['content'] = total_content
            luntan_list.append(review)
        except:
            print('the content is not normal')
    final_list = list()
    for comment in luntan_list:
        new_content = comment['content'].replace('\n', '').replace(' ', '')
        if new_content == "":
            print('no use')
        else:
            print('save')
            final_list.append(comment)
    return final_list


# 加载 Webdriver
spider = webdriver.Chrome('C:/Program Files (x86)/Chromedriver/chromedriver.exe')
spider.get('http://account.autohome.com.cn/login')
time.sleep(5)
# 帮助webdriver浏览器来login
user = spider.find_element_by_css_selector('#UserName')
user.send_keys('helloworld666')
password = spider.find_element_by_css_selector('#PassWord')
password.send_keys('password666')
# 休眠30秒的时间，以防出现需手动输入验证码的情况。如出现验证码，要在30秒内在浏览器内人工输入
time.sleep(30)
login = spider.find_element_by_css_selector('#SubmitLogin')
login.click()
time.sleep(5)
# 自己可以更改为自己感兴趣的汽车编号，这里65是宝马5系，197是奔驰E级，仅作测试和参考
car_code_list = ['65', '197']
# 获取并存储数据，论坛数据会被存储在car_code_luntan.json中，评价数据会被存储在car_code.json中
for car_code in car_code_list:
    print('We are working on car' + car_code)
    review_data = get_review_data(car_code=car_code, spider=spider)
    print('Finish analyzing the review data...')
    luntan_data = get_luntan_data(car_code=car_code, spider=spider)
    print('Finish analyzing the luntan data...')

    file_name = car_code + '.json'
    file = open(file_name, 'w', encoding="utf-8")
    json.dump(review_data, file, ensure_ascii=False)
    file.close()

    file_name = car_code + '_luntan.json'
    file = open(file_name, 'w', encoding="utf-8")
    json.dump(luntan_data, file, ensure_ascii=False)
    file.close()
