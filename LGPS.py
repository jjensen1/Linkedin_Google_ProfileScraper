#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a modification of the code sourced from this article: https://www.linkedin.com/pulse/how-easy-scraping-data-from-linkedin-profiles-david-craven/?trackingId=HUfuRSjER1iAyeWmcgHbyg%3D%3D
It is a web scraper scraping google for linkedin profiles; the use case would be recruiters sourcing target candidates for recruiting purposes. 

"""


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from bs4.element import Tag
from time import sleep
import csv
from parsel import Selector
import parameters
import numpy
import pandas as pd

# Function call extracting title and linkedin profile iteratively
def find_profiles(result_div):
    page_links = [] #reset the links found on the page
    for r in result_div:
        # Checks if each element is present, else, raise exception
        try:
            link = r.find('a', href=True)
            title = None
            title = r.find('h3')
            
            # returns True if a specified object is of a specified type; Tag in this instance 
            if isinstance(title,Tag):
                title = title.get_text()
    
            description = None
            description = r.find('span', attrs={'class': 'st'})
    
            if isinstance(description, Tag):
                description = description.get_text()
    
            # Check to make sure everything is present before appending
            if link != '' and title != '' and description != '':
                page_links.append(link['href'])
                #titles.append(title)
                #descriptions.append(description)
            
    
        # Next loop if one element is not present
        except Exception as e:
            print(e)
            continue
    
    return page_links
        
# This function iteratively clicks on the "Next" button at the bottom right of the search page. 
def profiles_loop():
    soup = BeautifulSoup(driver.page_source,'lxml')
    result_div = soup.find_all('div', attrs={'class': 'g'})
    
    page_links = find_profiles(result_div)
    
    next_button = driver.find_element_by_xpath('//*[@id="pnnext"]') 
    next_button.click()
    
    return page_links

def repeat_fun(times, f):
    for i in range(times): f()
      
# Gets information from a profile on linked-In 
def link_lookup(link):
    driver.get(link)
    sleep(0.5) #Maybe necessary to prevent a blockage from Linked-In
    sel = Selector(text=driver.page_source) 
    name = sel.xpath('//*[starts-with(@class,"inline t-24 t-black t-normal break-words")]/text()').extract_first()

    if name:
        name = name.strip()
        name_list = name.split(' ')
        LastName = name_list[-1]
        if len(name_list) < 3:
            FirstName = name_list[0]
        else:
            FirstName = name_list[0] + ' ' + name_list[1]
    else:
        FirstName = 'Not Found'
        LastName = 'Not Found'

    # xpath to extract the text from the class containing the job title
    job_title = sel.xpath('//*[starts-with(@class,"mt1 t-18 t-black t-normal break-words")]/text()').extract_first()

    if job_title:
        job_title = job_title.strip()
    else:
        job_title = 'Not found'

    # xpath to extract the text from the class containing the company
    company = sel.xpath('//*[starts-with(@class,"text-align-left ml2 t-14 t-black t-bold full-width lt-line-clamp lt-line-clamp--multi-line ember-view")]/text()').extract_first()

    if company:
        company = company.strip()
    else:
        company = 'Not found'

    # xpath to extract the text from the class containing the college
    # college = sel.xpath('//*[starts-with(@class,"text-align-left ml2 t-14 t-black t-bold full-width lt-line-clamp lt-line-clamp--multi-line ember-view")]/text()').extract_first()

    # xpath to extract the text from the class containing the location
    location = sel.xpath('//*[starts-with(@class,"t-16 t-black t-normal inline-block")]/text()').extract_first()

    if location:
        location = location.strip()
    else:
        location = 'Not found'

    #linkedin_url = driver.current_url Previous code to get links

    row={
        'FirstName': FirstName,
        'LastName': LastName,
        'Company Name': company,
        'Job Title': job_title,
        'location': location,
        'link':link, 
        'search': parameters.search_query
    }
    return row #Returns one row of information

if __name__ == '__main__':

    driver = webdriver.Chrome() #hopefully works using working directory

    # driver.get method() will navigate to a page given by the URL address
    driver.get('https://www.linkedin.com')

    # locate email form by_class_name
    username = driver.find_element_by_id('session_key')

    # send_keys() to simulate key strokes
    username.send_keys(parameters.linkedin_username)
    #sleep(0.5)

    # locate password form by_class_name
    password = driver.find_element_by_id('session_password')

    # send_keys() to simulate key strokes
    password.send_keys(parameters.linkedin_password)
    #sleep(0.5)

    # locate submit button by_class_name
    log_in_button = driver.find_element_by_class_name('sign-in-form__submit-button')

    # .click() to mimic button click
    log_in_button.click()
    #sleep(0.5)

    # driver.get method() will navigate to a page given by the URL address
    driver.get('https://www.google.com')
    #sleep(2)

    # locate search form by_name
    search_query = driver.find_element_by_name('q')

    # send_keys() to simulate the search text key strokes
    search_query.send_keys(parameters.search_query)

    # .send_keys() to simulate the return key 
    search_query.send_keys(Keys.RETURN)
    
    links = [] #Creates an empty list to collect the links

    for i in range(parameters.gpage_start, parameters.gpage_stop): #Starting and ending page for links
        rows = profiles_loop() #gets links to profiles from a google page, then select next page
        for item in rows: #add each link to the links list
            links.append(item)

    data = [] #Initial empty list for data
    for link in links:
        row = link_lookup(link)
        data.append(row)
    df = pd.DataFrame(data) #Convert data list to dataframe
    df.to_excel(parameters.file_name, index=False) #save dataframe as excel file
    print('finished')



