#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import redis
import logging
from Tor import Tor

class FinlandVisaScheduleCheck(object):
    check_page = r'http://visa.finland.eu/Russia/St_Petersburg/Schedule_an_Appointment1.html'
    MAX_WAIT = 3
    redis_channel = 'finland_visa_schedule_bot_channel'

    def __init__(self, phantomjs_path=None, redis_host=None, redis_port=None, proxy_host=None, proxy_port=None):
        self.phantomjs_path = phantomjs_path
        if not redis_host:
            redis_host = '127.0.0.1'
        if not redis_port:
            redis_port = 6379
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

    def init_wd(self, phantomjs_path=None, proxy_host=None, proxy_port=None):
        if phantomjs_path:
            service_args = []
            if proxy_host and proxy_port:
                service_args = [
                    '--proxy=%s:%s' % (proxy_host, proxy_port),
                    '--proxy-type=socks5',
                ]
            return webdriver.PhantomJS(executable_path=phantomjs_path, 
                                       service_log_path=os.path.devnull, 
                                       service_args=service_args)
        else:
            profile = webdriver.FirefoxProfile()
            if proxy_host and proxy_port:
                profile.set_preference('network.proxy.type', 1)
                profile.set_preference('network.proxy.socks', proxy_host)
                profile.set_preference('network.proxy.socks_port', proxy_port)
            return webdriver.Firefox(profile)

    def start_infinite_loop(self):
        self.driver = self.init_wd(self.phantomjs_path, self.proxy_host, self.proxy_port)
        while True:
            try:
                if not self.driver:
                    self.driver = self.init_wd(self.phantomjs_path, self.proxy_host, self.proxy_port)
                self.driver.get(self.check_page)
                self.driver.switch_to.frame(self.driver.find_element_by_tag_name('iframe'))
                WebDriverWait(self.driver, self.MAX_WAIT).until(EC.visibility_of_element_located((By.ID, 'ctl00_plhMain_cboVAC')))
                self.driver.find_element_by_xpath('//*[@id="ctl00_plhMain_cboVAC"]/option[text()="Consulate General of Finland, St. Petersburg"]').click()
                self.driver.find_element_by_id('ctl00_plhMain_btnSubmit').click()
                WebDriverWait(self.driver, self.MAX_WAIT).until(EC.visibility_of_element_located((By.ID, 'ctl00_plhMain_cboVisaCategory')))
                self.driver.find_element_by_xpath('//*[@id="ctl00_plhMain_cboVisaCategory"]/option[text()="Tourism"]').click()
                WebDriverWait(self.driver, self.MAX_WAIT).until(EC.visibility_of_element_located((By.ID, 'ctl00_plhMain_lblMsg')))
                msg = self.driver.find_element_by_id('ctl00_plhMain_lblMsg').text
                msg_time = '%s - %s' % (datetime.now(), msg)
                print msg_time
                self.redis.publish(self.redis_channel, msg)
            except:
                import sys, traceback
                exc_info = sys.exc_info()
                print exc_info[0], exc_info[1], exc_info[2]
                self.driver.quit()
                self.driver = None
                # add logging

if __name__ == '__main__':
    (ip, port) = sys.argv[1:3]
    tor = Tor(port)
    checker = FinlandVisaScheduleCheck(r'my_path_to_phantomjs', proxy_host=ip, proxy_port=port)
    checker.start_infinite_loop()