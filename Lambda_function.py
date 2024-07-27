import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    # Initialize the S3 client
    s3 = boto3.client('s3')
    
    # Define the bucket name and file key
    bucket_name = '23424421'
    file_key = 'test.json'
    
    # Retrieve query parameters from the event
    params = event.get('queryStringParameters', {})
    keyword = params.get('keyword', '').lower()
    start_date = params.get('start_date', '')
    end_date = params.get('end_date', '')
    #print("type of start_date",type(start_date),start_date)
    #print("type of end_date",type(end_date),end_date)
    
    
    # Get the object from S3
    try:
        s3_response = s3.get_object(Bucket=bucket_name, Key=file_key)
        file_content = s3_response['Body'].read().decode('utf-8')
        posts = json.loads(file_content)
        
        # Filter posts
        filtered_posts = []
        for post in posts['data']['children']:
            post_data = post['data']
            post_title = post_data.get('title', '').lower()
            post_selftext = post_data.get('selftext', '').lower()
            #post_created_utc = post_data.get('created_utc', 0)
            post_created_date = post_data.get('created_utc', 0)
            #print("type of created_date",type(post_created_date))
            #post_created_date = datetime.utcfromtimestamp(post_created_date)

            if keyword in post_title or keyword in post_selftext:
                if (not start_date or post_created_date >= start_date) and (not end_date or post_created_date <= end_date):
                    filtered_post = {
                        'post_selftext': post_selftext,
                        'post_author': post_data.get('author', ''),
                        'post_title': post_title,
                        #'post_created_utc': post_created_utc
                        'post_created_utc': post_created_date
                    }
                    filtered_posts.append(filtered_post)
        
        return {
            'statusCode': 200,
            'body': json.dumps(filtered_posts)
        }
        
    except s3.exceptions.NoSuchKey:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'The specified key does not exist.'})
        }
    except s3.exceptions.ClientError:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Access denied. Check your S3 bucket permissions.'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

if __name__ == '__main__':
    lambda_handler(None, None)
