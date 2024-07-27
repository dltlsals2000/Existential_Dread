import asyncio
import aiohttp
import json
import boto3
import datetime
import os
from dotenv import load_dotenv


async def fetch_reddit_posts(session, subreddit, start_date, end_date, most_recent_date):
    '''
    Fetch posts from a subreddit within a date range.
    '''
    posts = []
    after = None
    headers = {'User-agent': 'Mozilla/5.0'}

    while True:
        subreddit_url = 'https://www.reddit.com/r/' + subreddit + '/new' + '/.json'
        if after:
            subreddit_url += '?after=' + after 
        async with session.get(subreddit_url, headers=headers) as r:
            if r.status != 200:
                print(f'Error fetching data from {subreddit_url} with status code {r.status}')
                break
            data = await r.json()  # Parse JSON data

            # Adds the scraped data (fieldnames) into rows in our csv
            for post in data['data']['children']:
                post_data = post['data']
                post_date = datetime.datetime.fromtimestamp(post_data['created_utc'], datetime.timezone.utc)
                if most_recent_date and post_date <= most_recent_date:
                    # stop fetching posts if we reach the most recent date in S3
                    return posts
                
                if post_date < start_date:
                    # stop fetching posts if we reach the start date
                    return posts

                if post_data['selftext'] == '':
                    # skip the row if the post is empty
                    continue

                if start_date <= post_date <= end_date:
                    try:
                        filtered_post_data = {
                            'subreddit': post_data['subreddit'],
                            'selftext': post_data['selftext'],
                            'title': post_data['title'],
                            'author': post_data['author'],
                            'created_utc': post_data['created_utc'],
                            'url': post_data['url'],
                            'id': post_data['id'],
                            'score': post_data['score'],
                        }
                    except ValueError:
                        # skip the row if a field is missing 
                        continue
                
                    posts.append(filtered_post_data)

            after = data['data']['after']
            if not after:
                break
            await asyncio.sleep(4) # sleep for 4 seconds to avoid hitting Reddit's rate limit
    
    return posts

async def fetch_and_store_posts(subreddits, start_date, end_date, s3_object_name):
    '''
    Fetch and store posts from multiple subreddits.
    '''
    async with aiohttp.ClientSession() as session:
        tasks = []
        for subreddit in subreddits:
            most_recent_date = fetch_most_recent_date(S3_BUCKET_NAME, s3_object_name, subreddit)
            tasks.append(fetch_reddit_posts(session, subreddit, start_date, end_date, most_recent_date))
        
        results = await asyncio.gather(*tasks)
        existing_data = fetch_existing_data_from_s3(S3_BUCKET_NAME, s3_object_name)
        num_new_posts = 0
        for subreddit, posts in zip(subreddits, results):
            if not posts:
                print(f'No posts found for {subreddit}')
                continue
            existing_data.extend(posts)
            num_new_posts += len(posts)
            print(f'Fetched {num_new_posts} new posts from {subreddit}')
        
        print(f'Total number of posts fetched: {num_new_posts}')
        upload_to_s3(json.dumps(existing_data), S3_BUCKET_NAME, s3_object_name)

def fetch_most_recent_date(bucket_name, object_name, subreddit):
    '''
    Fetch the most recent date of a subreddit from an S3 bucket.
    '''
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_name)
        existing_data = json.loads(response['Body'].read().decode('utf-8'))

        if not existing_data:
            return None

        most_recent_date = max([datetime.datetime.fromtimestamp(post['created_utc'], datetime.timezone.utc) for post in existing_data if post['subreddit'] == subreddit])
        print(f'Most recent date for {subreddit}: {most_recent_date}')

        return most_recent_date
    except s3.exceptions.NoSuchKey:
        return None
    except Exception as e:
        print(f"Error fetching most recent date: {e}")
        return None


def fetch_existing_data_from_s3(bucket_name, object_name):
    '''
    Fetch a json object from an S3 bucket.
    '''
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_name)
        existing_data = json.loads(response['Body'].read().decode('utf-8'))
        return existing_data
    except s3.exceptions.NoSuchKey:
        return []
    except Exception as e:
        print(f"Error fetching existing data from S3: {e}")
        return []

def upload_to_s3(json_data, bucket_name, object_name=None):
    '''
    Upload a json data to an S3 bucket.
    '''
    try:
        s3.put_object(Bucket=bucket_name, Key=object_name, Body=json_data, ContentType='application/json')
        print(f'File uploaded to s3://{bucket_name}/{object_name}')
    except Exception as e:
        print(f'Error uploading file to s3://{bucket_name}/{object_name}')
        print(e)


# Load environment variables
load_dotenv()

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

def lambda_handler(event, context):
    subreddits = ["alberta", 'Edmonton', 'Calgary']

    # Fetch posts from the last 7 days for each subreddit
    end_date = datetime.datetime.now(datetime.timezone.utc)
    start_date = end_date - datetime.timedelta(days=7)

    object_name = f'reddit/posts.json'
    asyncio.run(fetch_and_store_posts(subreddits, start_date, end_date, object_name))


if __name__ == '__main__':
    lambda_handler(None, None)