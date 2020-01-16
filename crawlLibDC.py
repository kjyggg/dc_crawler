from selenium import webdriver
import pymysql


class crawlLibDC :

    def __init__(self):

        driver = webdriver.Chrome()
        driver.get()

        pymysql.conn