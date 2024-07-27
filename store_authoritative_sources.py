import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import boto3


# load environment variables
load_dotenv()

# AWS credentials
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# init S3 client
s3 = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN 
)

root_url = 'https://www.alberta.ca/'  


def extract_text_from_html(html_content):
    '''
    Extract text from an HTML content
    '''
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    return text


id = 0

def save_html_to_s3(url, html_content):
    global id

    text = extract_text_from_html(html_content)

    # save html to s3
    parsed_url = urlparse(url)
    path = 'alberta-gov/' + str(id) + '_' + parsed_url.path.strip('/').replace('/', '_')
    if not path:
        path = 'alberta-gov/index'
    file_name = f'{path}.txt'
    metadata = {
        'url': url
    }
    s3.put_object(Bucket=S3_BUCKET_NAME, Key=file_name, Body=text, ContentType='text/plain', Metadata=metadata)

    print(f"Saved {path} to S3")
    id += 1

def scrape_and_process(url, visited=set()):
    '''
    Scrape a URL and process the content recursively.
    '''
    if url in visited:
        return
    visited.add(url)
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text

        save_html_to_s3(url, html_content)

        soup = BeautifulSoup(html_content, 'html.parser')
        for link in soup.find_all('a', href=True):
            next_url = urljoin(url, link['href'])
            if urlparse(root_url).netloc in next_url and next_url not in visited:
                scrape_and_process(next_url, visited)

    except requests.RequestException as e:
        print(f'Error fetching {url}: {e}')

if __name__ == '__main__':
    scrape_and_process(root_url)