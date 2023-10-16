import json
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import hashlib
from scraper.constant import insertQuery,url_list
from scraper.executeQuery import insert_job_data


presentDate=datetime.now()

def open_chrome(url):
    chrome_options=webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
    
    driver=webdriver.Chrome(options=chrome_options)
    driver.get(url)
    return driver


def data_in_element(driver,selector,value):
    try:
        return driver.find_element(selector,value ).text
    except:
        return ''

#scrape data form the page
def targeted_data(driver,domain):
    jobData=[]
    jobSection = driver.find_elements(By.CLASS_NAME, 'up-card-list-section') #div contains all the job in multiple sections
    for job in jobSection:# get individual job data
        try:
            jobTitle =data_in_element(job,By.CLASS_NAME,'p-sm-right')
            jobDescription = data_in_element(job,By.CSS_SELECTOR,'[data-test="job-description-text"]') 
            jobTagArray = data_in_element(job,By.CSS_SELECTOR,'.up-skill-wrapper')
            jobTag = json.dumps(jobTagArray.split('\n'))
            jobTier = data_in_element(job,By.CSS_SELECTOR,'[data-test="contractor-tier"]') 
            jobPostedOn = data_in_element(job,By.CSS_SELECTOR,'[data-test="UpCRelativeTime"]')
            jobType = data_in_element(job,By.CSS_SELECTOR, '[data-test="job-type"]') 
            jobBudgetOrDuration = data_in_element(job,By.CSS_SELECTOR, '[data-test="budget"]') 
            if not jobBudgetOrDuration:
                jobBudgetOrDuration =data_in_element(job,By.CSS_SELECTOR, '[data-test="duration"]') 
            hashEncode= (jobTitle+jobTag+domain).encode('utf-8')

            pageData = {
                "job": jobTitle,
                "description": jobDescription,
                "tag": jobTag,
                "tier": jobTier,
                "type": jobType,
                "scrapedOn": presentDate,
                "postedOn": jobPostedOn,
                "budgetOrDuration": jobBudgetOrDuration,
                "domain": domain,
                "hashKey": hashlib.md5(hashEncode).hexdigest()
            }

            jobData.append(pageData)
        except Exception as e:
            print(f"Error scraping job: {str(e)}")
    time.sleep(2)
    return jobData

# check if the actual page loaded or "verify human" and handle it
def verify_page_loaded(driver,domain,retryUrl,retryCount=3):
    try:
        WebDriverWait(driver,15).until(EC.presence_of_element_located((By.CLASS_NAME, 'p-sm-right')))
        return targeted_data(driver,domain)
    except:
        if retryCount > 0:
            try:
                WebDriverWait(driver,5).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[title='Widget containing a Cloudflare security challenge']")))
                WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label.ctp-checkbox-label"))).click()
                return verify_page_loaded(retryDriver,domain,retryUrl,retryCount-1)
            except:
                print("Unable to scrape the page, reloading the page.")
                try:
                    retryDriver = open_chrome(retryUrl)
                    return verify_page_loaded(retryDriver,domain,retryUrl,retryCount-1)
                except Exception as inner_exception:
                    print(f"Error during verify: {str(inner_exception)}") 
    return[]


def scraper( domain, url):
    driver = open_chrome(url)
    return verify_page_loaded(driver,domain,url)   

# traverse to pages
def multi_page_scraper(pageUrl,domain):
    totalJobs = []
    for index in range(1,51):
        url = f'{pageUrl}&page={index}'
        jobData=scraper(domain,url)
        if jobData:
            totalJobs+=jobData
        print(f'-------------------data scraped from page {index}-------------------')
    return totalJobs

# Main Function
def main(pageUrl,domain):
    finalJobData = multi_page_scraper(pageUrl,domain)
    insert_job_data(insertQuery,finalJobData)

if __name__ == "__main__":
    for data in url_list:
        main(data[0],data[1])   

