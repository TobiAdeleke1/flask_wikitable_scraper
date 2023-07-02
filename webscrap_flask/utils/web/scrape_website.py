import requests
from typing import List
from bs4 import BeautifulSoup
import lxml
import re
import os
import pandas as pd


def get_response(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return ''


def get_beautiful_soup(response_text: str):
    return BeautifulSoup(response_text, 'lxml')

def get_all_by_class(soup):
    return soup.find_all(attrs={"class":"wikitable"})

def get_str_of_table(table):
    return repr(table)

def get_html_table_list(str_table:str): 
    return pd.read_html(str_table, header=0)

def get_table_pf(df_list): 
    return pd.concat(df_list)

def get_filename(soup):
    excel_title= f'{slugify(str(soup.title.string))}_output.xlsx'
    return excel_title

def slugify(s):
  s = s.lower().strip()
  s = re.sub(r'[^\w\s-]', '', s)
  s = re.sub(r'[\s_-]+', '_', s)
  s = re.sub(r'^-+|-+$', '', s)
  return s

def get_section_name(table):
 
    table_caption = [con_name.string for con_name in table.contents if con_name.name =='caption']
    if table_caption:
        caption_string = table_caption[0].strip()
        sheet_name = caption_string[:20]
    else:
        table_h2_list = [elem for elem in table.previous_siblings if elem.name=='h2']
        # print("table_h2_list", table_h2_list)
        string_h2 = list(table_h2_list[0].find_all("span",class_="mw-headline")[0].strings)
        sheet_name = string_h2[0][:20]
    
    return slugify(sheet_name)



def main_run(url:str, store_path:str):
    print("request url",url)
    reponse = get_response(url.strip())

    if not reponse:
        return 'Error: URL RETURNED NONE'
    
    response_soup = get_beautiful_soup(reponse)
  
    wikitable_list = get_all_by_class(response_soup)

    if not wikitable_list:
        return 'Warning, wiki contains no table'
    
    filename = get_filename(response_soup)
 
  
    storage_url = os.path.join(store_path,filename)
    print('App FILE STORAGE AT!!!!', storage_url)
   
    # print('STOREPATH !!!', storage_url, path,store_path, filename)
    writer = pd.ExcelWriter(storage_url, engine="xlsxwriter")


    for table in wikitable_list:
        formatted_table = get_str_of_table(table)
        formatted_table_list = get_html_table_list(formatted_table)
        formatted_table_df = get_table_pf(formatted_table_list)
        section_name = get_section_name(table)
        # write to sheet
        formatted_table_df.to_excel(writer, sheet_name=section_name)
    writer.close() # can just use a context manager
    # return storage_url
    return filename, storage_url



# class SoupUtil:
#     def __init__(self, soup):
#         self.soup = soup

    
    
#     def get_section_name(self, tag) -> str:
#     #Get caption or Heading
#         pass