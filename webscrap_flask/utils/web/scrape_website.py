import requests
from typing import List
from bs4 import BeautifulSoup
import lxml
import re
import os
import pandas as pd
import logging


def get_response(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to fetch URL: {url} - {e}")
        return ''


def get_beautiful_soup(response_text: str) -> BeautifulSoup:
    return BeautifulSoup(response_text, 'lxml')


def find_all_by_class(soup: BeautifulSoup, class_name: str) -> List:
    return soup.find_all(class_=class_name)


def get_table_string(table: BeautifulSoup) -> str:
    return repr(table)


def parse_html_table(html_table: str) -> List[pd.DataFrame]:
    return pd.read_html(html_table, header=0)


def concatenate_dataframes(df_list: List[pd.DataFrame]) -> pd.DataFrame:
    return pd.concat(df_list)


def generate_filename(soup: BeautifulSoup) -> str:
    title = soup.title.string if soup.title else 'Untitled'
    slugified_title = slugify(title)
    return f'{slugified_title}_output.xlsx'


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '_', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text


def extract_section_name(table: BeautifulSoup) -> str:
    table_caption = table.caption
    if table_caption:
        caption_string = table_caption.string.strip()
        return slugify(caption_string[:20])
    else:
        h2_elements = table.find_previous_siblings('h2')
        if h2_elements:
            section_name = h2_elements[0].find('span', class_='mw-headline')
            if section_name:
                return slugify(section_name.string[:20])
    return ''


def main_run(url: str, store_path: str):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    
    logger.info("Request URL: %s", url)
    response = get_response(url.strip())

    if not response:
        logger.error("Error: URL returned none")
        return 'Error: URL returned none'

    response_soup = get_beautiful_soup(response)

    wikitable_list = find_all_by_class(response_soup, 'wikitable')

    if not wikitable_list:
        logger.warning("Warning: Wiki contains no table")
        return 'Warning: Wiki contains no table'

    filename = generate_filename(response_soup)

    storage_path = os.path.join(store_path, filename)
    logger.info('App File Storage at: %s', storage_path)

    try:
        with pd.ExcelWriter(storage_path, engine='xlsxwriter') as writer:
            for table in wikitable_list:
                table_str = get_table_string(table)
                table_data = parse_html_table(table_str)
                if not table_data:
                    logger.warning("No data found in table")
                    continue
                table_df = concatenate_dataframes(table_data)
                section_name = extract_section_name(table)
                if not section_name:
                    logger.warning("Section name not found")
                    section_name = 'Untitled'
                table_df.to_excel(writer, sheet_name=section_name)

        logger.info('Excel file created successfully')
        return filename, storage_path

    except Exception as e:
        logger.error(f"An error occurred during Excel file generation: {e}")
        return 'Error: Excel file generation failed'














