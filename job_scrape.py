#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 23:29:48 2020

@author: takutakamatsu
"""
import pandas as pd
from requests import get
from bs4 import BeautifulSoup
from datetime import date
import dateutil.relativedelta
import time
from pyvirtualdisplay import Display #PythonAnywhere
from selenium import webdriver
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import secret

def ent_careers():
    '''scrapes all job listings with keyword 'data' from Entertainment Careers and returns dataframe'''

    base_url = 'https://www.entertainmentcareers.net/2/search/search2.asp?zoom_query=data&FULLORPART=-1&JOBSTATE=NY&zoom_page=1&zoom_per_page=100&zoom_cat=-1&zoom_and=0&zoom_sort=0'
    url = 'https://www.entertainmentcareers.net/2/search/search2.asp?zoom_query=data&FULLORPART=-1&JOBSTATE=NY&zoom_page={}&zoom_per_page=100&zoom_cat=-1&zoom_and=0&zoom_sort=0'
    response = get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")
    #find number of pages
    pages = int(soup.find("div", class_="result_pagescount").text.split(' ')[0])

    job_list = []
    #loop through each page
    for page in range(1, pages+1):

        soup = BeautifulSoup(get(url.format(page)).text, "html.parser")

        #for every job listing - main block
        for container in soup.find_all('div', class_='result_block'):

            job_url = 'https://www.entertainmentcareers.net'+container.a['href']
            heading = container.a.text.split(' - (')
            title = str(heading[0].strip())
            company = str(heading[1].split('-')[1].strip())
            location = str(heading[1].split('-')[2].strip())

            job_type = container.find('span', class_='category').text.strip()[1:-1]
            #try to get posted date if visible in description

            try:
                context_list = container.find('div', class_='context').text.split(' ')
                posted_date = ' '.join(context_list[context_list.index('Posted:')+1 : context_list.index('Posted:')+4])
            except:
                posted_date = None

            job_list.append((title, company, location, job_type, job_url, posted_date))

        #for every job listing - altblock
        for container in soup.find_all('div', class_='result_altblock'):

            job_url = 'https://www.entertainmentcareers.net'+container.a['href']
            heading = container.a.text.split(' - (')
            title = str(heading[0].strip())
            company = str(heading[1].split('-')[1].strip())
            location = str(heading[1].split('-')[2].strip())

            job_type = container.find('span', class_='category').text.strip()[1:-1]
            #try to get posted date if visible in description

            try:
                context_list = container.find('div', class_='context').text.split(' ')
                posted_date = ' '.join(context_list[context_list.index('Posted:')+1 : context_list.index('Posted:')+4])
            except:
                posted_date = None

            job_list.append((title, company, location, job_type, job_url, posted_date))

    #return jobs as dataframe
    job_df = pd.DataFrame.from_records(job_list, columns=['Title', 'Company', 'Location', 'Job Type', 'Job URL', 'Posted Date'])
    return job_df

#builtinnyc
def builtinnyc():
    '''scrapes Built In NYC's job listings with keywords "data analytics" and "python", returning dataframe'''

    #search for data analytics + python in dev/engineer field
    base_url = 'https://www.builtinnyc.com/jobs?f%5B0%5D=job-category_developer-engineer-python&f%5B1%5D=job-category_data-analytics&f%5B2%5D=level_entry'
    url = 'https://www.builtinnyc.com/jobs?f%5B0%5D=job-category_developer-engineer-python&f%5B1%5D=job-category_data-analytics&f%5B2%5D=level_entry&page={}'
    soup = BeautifulSoup(get(base_url).text, "html.parser")

    #find number of pages
    pager_items = soup.find_all('li', class_="pager__item")
    pages = int(max([page.text.split(' ')[-1].strip() for page in pager_items if page.text.split(' ')[-1].strip().isnumeric()]))

    job_lists = []
    #loop through pages (starts at 0)
    for page in range(pages):
        soup = BeautifulSoup(get(url.format(page)).text, "html.parser")
        #find all job containers
        for container in soup.find_all("div", class_="views-row"):
            title = container.find("h2", class_="title").text.strip()
            company = container.find("div", class_="company-title").text.strip()
            location = container.find("div", class_="job-location").text.strip()
            description = container.find("div", class_="description").text
            job_url = 'https://builtinnyc.com' + str(container.find("div", class_="wrap-view-page").find('a')['href'])

            job_lists.append((title, company, location, description, job_url))

    #return as dataframe
    job_df = pd.DataFrame.from_records(job_lists, columns=['Title', 'Company', 'Location', 'Description', 'Job URL'])
    return job_df


def linkedin():
    ''' scrapes LinkedIn using Selenium - dynamically scrolling down the page and returning dataframe
        Search term: data anlytics
        Location: New York City
        Range: up to 1-month
    '''
    #LinkedIn Jobs, not signed in, refreshes dynamically using Javascript. We can use Selenium to physically scroll through the page as it's loading

    #set Chrome to headless -- to work with PythonAnywhere
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    #open headless Chrome
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get('https://www.linkedin.com/jobs/search?keywords=Data%2BAnalyst&location=New%2BYork%2C%2BUnited%2BStates&trk=public_jobs_jobs-search-bar_search-submit&f_PP=102571732&f_E=2%2C3&sortBy=DD&f_TP=1%2C2%2C3%2C4&redirect=false&position=1&pageNum=0')
        print("Opened:", driver.title)
        time.sleep(5)

        #check for pop-ups and click dismiss if found
        try:
            driver.find_element_by_xpath('//button[@class="cta-modal__dismiss-btn"]').click()
        except:
            pass

        #display number of job listings to scrape
        num_jobs = driver.find_element_by_xpath('//span[@class="results-context-header__job-count"]').text.replace(',', '').replace('+', '')
        print("Number of results to scrape:", num_jobs)

        jobs = []
        results = 1
        while True:
            #check for 'load more' button
            try:
                driver.find_element_by_xpath('//button[contains(@aria-label, "Load more results")]').click()
                time.sleep(3)
            except:
                pass

            #scroll
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

            #find loaded containers
            loaded = driver.find_elements_by_xpath('//li[contains(@class,"job-result-card")][position()>=' + str(results) + ']')
            print("loaded:", len(loaded), "jobs")

            #append loaded containers to results counter
            results += len(loaded)

            #loop through each container and append search results to list
            for idx, container in enumerate(loaded):
                title = container.find_element_by_xpath('.//h3[contains(@class, "result-card__title")]').text
                company = container.find_element_by_xpath('.//h4[contains(@class, "result-card__subtitle")]').text
                location = container.find_element_by_xpath('.//span[@class="job-result-card__location"]').text
                posted_date = container.find_element_by_xpath('.//time[contains(@class,"job-result-card__listdate")]').get_attribute('datetime')
                job_href = container.find_element_by_xpath('.//a[@class="result-card__full-card-link"]').get_attribute('href')

                jobs.append((title, company, location, posted_date, job_href))

            print("total scraped:", results)

            #if results count matches number of results, break loop
            if results >= int(num_jobs):
                break

        #create dataframe with job list
        jobs_df = pd.DataFrame.from_records(jobs, columns=['Title', 'Company', 'Location', 'Posted Date', 'Job URL'])
        #return dataframe
        return jobs_df

    finally:
        driver.quit()

def angellist():
    ''' scrapes Angel List using Selenium, dynamically scrolling down the page whilst extracting key job insights
        search term: data analytics
        returns dataframe of current job listings
    '''
    #as AngelList is dynamic, we'll have to use Selenium
    #set Chrome to headless
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    #open Chrome with Selenium
    driver = webdriver.Chrome(options=chrome_options)

    try:
        #try login if not already
        try:
            driver.get('https://angel.co/login')
            driver.find_element_by_id('user_email').send_keys(secret.login_email())
            driver.find_element_by_id('user_password').send_keys(secret.login_password())
            driver.find_element_by_xpath('/html/body/div[1]/div[4]/div/div/div/div/div/div[1]/div[1]/form/div[2]/input').click()
            print("Opened:", driver.title)
            time.sleep(5)
        except:
            pass
        #number of results
        num_results = int(driver.find_element_by_xpath('//*[@id="main"]/div/div[5]/div[2]/div/div[3]/h4').text.split(' ')[0])
        print("Number of results:", num_results)

        jobs = []
        results = 1
        while True:
            #scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #let the page load
            time.sleep(3)

            #find loaded components / for position where new
            loaded_posts = driver.find_elements_by_xpath('//div[@class="component_4d072"][position()>=' + str(results) + ']')
            print("loaded posts:", len(loaded_posts))
            #add length of loaded posts to results to only scrape new daa
            results += len(loaded_posts)

            #loop through each loaded post
            for post in loaded_posts:
                title = post.find_element_by_class_name("title_2148e").text
                company = post.find_element_by_xpath('.//a[@class="component_21e4d defaultLink_7325e name_5fa89"]').text
                try:
                    salary_estimate = post.find_element_by_class_name("salaryEstimate_b0878").text
                except:
                    salary_estimate = ''
                try:
                    description = post.find_element_by_xpath('.//span[@class="subheader_755b1"]').text
                except:
                    description = ''

                #grab location, remove salary from scrape and convert list to comma-separated list
                location = list(filter(None, post.find_element_by_xpath('.//span[contains(@class,"__halo_fontSizeMap_size--sm __halo_color_slate--900")]').text.replace(salary_estimate, '').split(' • ')))
                location = ", ".join(location)

                #dates are relative to the current date - subtract it to find an estimated post date
                try:
                    posted_date_relative = post.find_element_by_xpath('.//span[contains(@class,"tablet_6074f")]').text.split(' ')
                    if posted_date_relative[0].lower() == 'this':
                        posted_date = date.today() - dateutil.relativedelta.relativedelta(days=4)
                    elif posted_date_relative[0].lower() == 'yesterday':
                        posted_date = date.today() - dateutil.relativedelta.relativedelta(days=1)
                    elif posted_date_relative[1].lower() == 'weeks' or posted_date_relative[1].lower() == 'week':
                        posted_date = date.today() - dateutil.relativedelta.relativedelta(weeks=int(posted_date_relative[0]))
                    elif posted_date_relative[1].lower() == 'weeks' or posted_date_relative[1].lower() == 'week':
                        posted_date = date.today() - dateutil.relativedelta.relativedelta(weeks=int(posted_date_relative[0]))
                    elif posted_date_relative[1].lower() == 'months'or posted_date_relative[1].lower() == 'month':
                        posted_date = date.today() - dateutil.relativedelta.relativedelta(months=int(posted_date_relative[0]))
                    elif posted_date_relative[1].lower() == 'days'or posted_date_relative[1].lower() == 'day':
                        posted_date = date.today() - dateutil.relativedelta.relativedelta(days=int(posted_date_relative[0]))
                except:
                    posted_date = ''

                #get job url
                job_url = post.find_element_by_xpath('.//div[@class="component_07bb9"]/a').get_attribute('href')
                #append all to list
                jobs.append((title, company, description, location, str(posted_date), salary_estimate, job_url))

            #number of results scraped
            print("total scraped", results)

            #if results count matches number of results, break loop
            if results >= num_results:
                break

        #convert list to dataframe
        jobs_df = pd.DataFrame.from_records(jobs, columns=['Title', 'Company','Description', 'Location', 'Posted Date', 'Salary Estimate', 'Job URL'])

        #return dataframe
        return jobs_df

    finally:
        driver.quit()

def combine_jobs(ent_careers, built_in_nyc, linkedin, angellist):
    #add website name to each dataframe
    ent_careers.loc[:,'Website'] = 'Entertainment Careers'
    built_in_nyc.loc[:, 'Website'] = 'Built In NYC'
    linkedin.loc[:, 'Website'] = 'LinkedIn'
    angellist.loc[:, 'Website'] = 'Angel List'

    #concatenate all posts
    all_jobs = pd.concat([ent_careers, built_in_nyc, linkedin, angellist])
    all_jobs = all_jobs[['Title', 'Company', 'Location', 'Description', 'Salary Estimate', 'Job Type', 'Posted Date', 'Website', 'Job URL']]

    #deduplicate jobs by title and company name, keeping most recent occurence
    all_jobs.drop_duplicates(['Title', 'Company'], keep='first', inplace=True)

    #return combined dataframe
    return all_jobs

def write_to_gsheets(df):
    gc = gspread.service_account('service_account.json')
    sheet = gc.open("Taku-data_job_scraper").sheet1

    #sort by date
    df['Posted Date'] = pd.to_datetime(df['Posted Date'])
    df = df.sort_values('Posted Date', ascending=False)

    #fill null with empty string
    df.fillna('', inplace=True)

    #update google sheets
    set_with_dataframe(sheet, df)


def main():
    #initiate global variables
    global ent_careers
    global built_in_nyc
    global linkedin
    global angellist

    #calculate scrape time
    start_time = time.time()
    ent_careers = ent_careers()
    elapsed = time.time() - start_time
    print("Returned Entertainment Career; ", len(ent_careers), " results on ", date.today(), ". Took ", format(elapsed, ".2f"), " seconds", sep="")

    start_time = time.time()
    built_in_nyc = builtinnyc()
    elapsed = time.time() - start_time
    print("Returned Built In NYC; ", len(built_in_nyc), " results on ", date.today(), ". Took ", format(elapsed, ".2f"), " seconds", sep="")

    start_time = time.time()
    linkedin = linkedin()
    elapsed = time.time() - start_time
    print("Returned LinkedIn; ", len(linkedin), " results on ", date.today(), ". Took ", format(elapsed, ".2f"), " seconds", sep="")

    start_time = time.time()
    angellist = angellist()
    elapsed = time.time() - start_time
    print("Returned AngelList; ", len(angellist), " results on ", date.today(), ". Took ", format(elapsed, ".2f"), " seconds", sep="")

    #combine all dataframes and deduplicate
    all_jobs = combine_jobs(ent_careers, built_in_nyc, linkedin, angellist)

    #write to spreadsheet
    write_to_gsheets(all_jobs)

if __name__ == '__main__':
    main()

