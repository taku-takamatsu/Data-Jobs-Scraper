# Data Jobs Scraper
This project scrapes "Data Analyst" job listings from LinkedIn, AngelList, Built In NYC and Entertainment Careers. I've narrowed down the search area to include jobs only located in New York City or are remote, and have placed a criteria to look for "entry-level" or "associate" positions. For LinkedIn, I've set a maximum search time-frame of a month till the scrape date.

## Project Description
The main purpose of this project is to demonstrate foundational web-scraping skills using BeautifulSoup and Selenium. As a graduating Senior, I'm currently in the midst of my job-hunt, so I thought it was natural for me to compile a list of relevant job openings that may help my search. This list updates daily (scheduled on PythonAnywhere).

[Entertainment Careers](https://www.entertainmentcareers.net/2/search/search2.asp?zoom_query=data&FULLORPART=-1&JOBSTATE=NY&zoom_page=1&zoom_per_page=100&zoom_cat=-1&zoom_and=0&zoom_sort=0) and [Built In NYC](https://www.builtinnyc.com/jobs?f%5B0%5D=job-category_developer-engineer-python&f%5B1%5D=job-category_data-analytics&f%5B2%5D=level_entry&page=1) uses BeautifulSoup as they're static web-pages that allow pagination by adjusting HTML parameters.
[LinkedIn](https://www.linkedin.com/jobs/search?keywords=Data%2BAnalyst&location=New%2BYork%2C%2BUnited%2BStates&trk=public_jobs_jobs-search-bar_search-submit&f_PP=102571732&f_E=2%2C3&sortBy=DD&f_TP=1%2C2%2C3%2C4&redirect=false&position=1&pageNum=0) and [AngelList](https://angel.co/jobs) are both dynamic websites written in Javascript that utilize some form of infinite scrolling. In this case, Selenium is used to automate web interactions - scrolling down the page and extracting job-features on the go. 
After scraping all the websites, I've deduplicated any reoccurring job listings, and have exported it to Google sheets via Google Drive's API. 

## Files
* [job-scraper.py](https://github.com/taku-takamatsu/Data-Jobs-Scraper/blob/master/job_scraper.py): Full code to scrape all 4 websites and dump results to Googe sheets.
* [Search Results - Google Sheets](https://docs.google.com/spreadsheets/d/1y23F2L5V50pGFvjTTIXZO9dX3-mt6ucqT2Lof4HkEsY/edit?usp=sharing): The result of the scrape has been dumped to this google sheets.

## Contact
* Taku's [LinkedIn](https://www.linkedin.com/in/taku-takamatsu/)
