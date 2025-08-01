import subprocess
import uuid,os,json
from fastapi import FastAPI,Form
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
from langchain_postgres import PGVector

def create_unique_name():
    try:
        unique_file_name = str(uuid.uuid4()) + '.json'
        return os.path.join('urlcrawler','result_files',unique_file_name)
    except Exception as e:
        print('Exception in unique name :::: ',e)


def run_scrapy_spider(start_urls):
    try:
        allowed_domains = get_domain_name(start_urls)
        file_name = create_unique_name()
        command = ["python", "/Users/shubhamrajpurohit/Desktop/chatbot_webscraper/scrapperchatbot/urlcrawler/urlcrawler/spiders/crawlspider.py",
                    "--output_file", file_name,
                    "--start_urls", start_urls,
                    "--allowed_domains", allowed_domains]
        subprocess.run(command, check=True)
        return read_file(file_name)
    except subprocess.CalledProcessError as e:
        print("Error running scrapy spider:", e)

def get_domain_name(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            content = json.loads(content)
        return content
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return f"An error occurred: {str(e)}"



# x=vector_store.similarity_search(
#     "we help you make smart",
#     k=3,
# )
# print(x)
