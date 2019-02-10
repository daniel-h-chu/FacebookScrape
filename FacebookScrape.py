# Instructions at bottom of this file

import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import pandas as pd


def scroll(driver, time_length):
    scroll_time = 1
    driver.execute_script("return document.body.scrollHeight")
    for i in range(int(time_length)):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_time)
        driver.execute_script("return document.body.scrollHeight")


def authenticate(driver, friend_page, email, password):
    driver.get(friend_page)
    WebDriverWait(driver, 3).until(expected_conditions.presence_of_element_located(
        (By.ID, 'email')))
    driver.find_element_by_id('email').send_keys(
        email)
    driver.find_element_by_id('pass').send_keys(
        password)
    driver.find_element_by_id('loginbutton').click()


def findMyFriends(driver, friend_page, num_friends, email, password):
    friend_links = []
    friend_names = []
    friend_dict = {}
    authenticate(driver, friend_page, email, password)
    driver.get(friend_page)
    scroll(driver, num_friends / 20)
    raw_html = driver.page_source
    html = BeautifulSoup(raw_html, 'html.parser')
    for link in html.find_all("div", class_="fsl fwb fcb"):
        try:
            l = link.contents[0].get_text()
            s = link.next_sibling.get('href')
            friend_links.append(s)
            friend_names.append(l)
        except AttributeError:
            continue
    for link, name in zip(friend_links, friend_names):
        try:
            if link[:8] != '/browse/':
                friend_dict[name] = link
                print(link, name)
        except TypeError:
            continue
    dffff = pd.Series(friend_dict)
    dffff.to_csv("Friend Links.csv")
    return friend_dict


def readFriendLinks(csv="Friend Links.csv"):
    df = pd.read_csv(csv)
    dct = {}
    for i in range(df.index.size):
        dct[df.iloc[i, 0]] = df.iloc[i, 1]
    return dct


def getMutual(driver, friend_dict_full, friend_page, email, password, max_mutual_friends):
    friend_dict = friend_dict_full
    friend_num = {}
    edge_list = []
    for index, name in enumerate(friend_dict.keys()):
        friend_num[name] = index
    for index, name in enumerate(friend_dict.keys()):
        print(str(index) + ' out of ' + str(len(friend_dict.keys())))
        driver.get(friend_dict[name])
        raw_html = driver.page_source
        html = BeautifulSoup(raw_html, 'html.parser')
        scroll(driver, max_mutual_friends/20)
        for link in html.find_all("div", class_="fsl fwb fcb"):
            try:
                edge_list.append([friend_num[name], friend_num[link.contents[0].get_text()]])
            except KeyError:
                continue
    pd.DataFrame(edge_list).to_csv("EdgeList.csv", header=False, index=False)
    pd.Series(friend_num).to_csv("NodeList.csv", index=True)


def webscrape(my_friend_page, email, password, num_friends, max_mutual_friends):
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    findMyFriends(driver, my_friend_page, num_friends, email, password)
    friend_dict = readFriendLinks()
    getMutual(driver, friend_dict, my_friend_page, email, password, max_mutual_friends)


#
# Have Fun Webscraping!
#
# my_friend_page - Your Friend Page on Facebook (Page with all your friends on it. Goto the friends tab on facebook.com)
# email - Your Email to log into Facebook
# password - Your Password to log into Facebook
# num_friends - Rough estimate of how many friends you have (Overestimate is better)
# max_mutual_friends - Number of mutual friends of your friend with the most mutual friends (Determines how long to
# scroll for)
#
webscrape(
    my_friend_page='',
    email='',
    password='',
    num_friends=1,
    max_mutual_friends=1
    )
