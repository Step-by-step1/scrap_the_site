from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from datetime import datetime
from datetime import date
from datetime import timedelta
import pandas as pd
def extract_content(URL, margin, date_count):
    html = urlopen(URL)
    bs = BeautifulSoup(html, features="html.parser")
    today = datetime.today()
    margin = timedelta(days=margin)
    if bs.find("div", {"id":re.compile("projectp(0-9)*")}):
        print("Scrapping project / vacancy...")
        published = bs.find("div", text=re.compile("Опубликован:"))
        if published:
            raw_date = list(published.next_siblings)[1].get_text().split("|")[0].strip("\n").strip(" ")
            date_published = datetime.strptime(raw_date, '%d.%m.%Y')
            if today - margin < date_published:
                date_count = 0
                return bs.find("div", {"id":re.compile("projectp(0-9)*")}).get_text(), date_count
            else:
                date_count += 1
                print("\n\n\nThis job is older than set margin! Date_count = {}\n\n\n".format(date_count))
                return bs.find("div", {"id":re.compile("projectp(0-9)*")}).get_text(), date_count
        else:
            print("\n\n\nNo date information extracted!\n\n\n")
            return bs.find("div", {"id":re.compile("projectp(0-9)*")}).get_text(), date_count
    elif bs.find("div", {"id":re.compile("contest_info_(0-9)*")}):
        print("Scrapping contest...")
        published = bs.find("div", {"class":"const-head"}).find("div", {"class":"contest-e"})
        if published:
            raw_date = list(published.children)[-1].strip("\n").strip(" ").strip("[").split("|")[0].strip(" ")
            date_published = datetime.strptime(raw_date, '%d.%m.%Y')
            if today - margin < date_published:
                date_count = 0
                if len(bs.find("div", {"id":re.compile("contest_info_(0-9)*")}).findAll("div", {"class":"contest-body"})) > 1:
                    return bs.find("div", {"id":re.compile("contest_info_(0-9)*")}).findAll("div", {"class":"contest-body"})[1].get_text(), date_count
                else:
                    return "UNABLE TO EXTRACT", date_count
            else:
                date_count += 1
                print("\n\n\nThis job is older than set margin! Date_count = {}\n\n\n".format(date_count))
                if len(bs.find("div", {"id":re.compile("contest_info_(0-9)*")}).findAll("div", {"class":"contest-body"})) > 1:
                    return bs.find("div", {"id":re.compile("contest_info_(0-9)*")}).findAll("div", {"class":"contest-body"})[1].get_text(), date_count
                else:
                    return "UNABLE TO EXTRACT", date_count
        else:
            print("\n\n\nNo date information extracted!\n\n\n")
            if len(bs.find("div", {"id":re.compile("contest_info_(0-9)*")}).findAll("div", {"class":"contest-body"})) > 1:
                return bs.find("div", {"id":re.compile("contest_info_(0-9)*")}).findAll("div", {"class":"contest-body"})[1].get_text(), date_count
            else:
                return "UNABLE TO EXTRACT", date_count
    else:
        print("Returning nothing...")
        return "UNABLE TO EXTRACT", date_count

def scrap_the_page(URL, page, data_dict, margin, date_count):
    html = urlopen(URL + "/projects/" + page)
    bs = BeautifulSoup(html, features="html.parser")
    list_of_jobs = bs.findAll("div", {"id": re.compile("project-item(0-9)*")})
    print("Length of list of jobs is {}.".format(len(list_of_jobs)))
    for item in list_of_jobs:
        name = item.find("a", {"id": re.compile("prj_name_(0-9)*")})
        if name:
            if 'href' in name.attrs:
                print("{} adding to a dictionary...{}".format(name["id"], name.get_text()))
                description, date_count = extract_content((URL + name.attrs['href']), margin, date_count)
                data_dict["Project ID"].append(name["id"])
                data_dict["Job Title"].append(name.get_text())
                data_dict["Job Description"].append(description)
            else:
                description = "UNABLE TO EXTRACT"
                data_dict["Project ID"].append(name["id"])
                data_dict["Job Title"].append(name.get_text())
                data_dict["Job Description"].append(description)
    return bs, data_dict, date_count

def scrap_the_site(URL, margin):
    date_count = 0
    count = 1
    page = ""
    data_dict = {"Project ID":[], "Job Title": [], "Job Description": []}
    while URL and date_count < 10:
        print("Scrapping page({}) ...({}/projects/{})".format(count, URL, page))
        bs, data_dict, date_count = scrap_the_page(URL, page, data_dict, margin, date_count)
        list_of_links = bs.find("div", {"class":"b-pager"}).findAll("a", {"class":"b-pager__link"})
        
        print("Length of data_dict is {}.".format(len(data_dict)))
        count += 1
        if len(list_of_links) > 1 or page == "":
            page = list_of_links[-1]["href"]
        else:
            URL= None
    df = pd.DataFrame(data_dict)
    new_file_name = input("Please enter the name of csv file to save the data:  ")
    while not re.match("(\w?[A-Za-z0-9]+\w?)+", new_file_name):
        print("You've entered invalid file name!")
        new_file_name = input("Please enter a VALID name of csv file to save the data:  ")
        
    df.to_csv(new_file_name + ".csv")
    return df
                
        
    
            
        
