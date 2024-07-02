import logging,json,sys,os,csv,glob,sqlite3,csv,re,time,boto3,shutil
#AWS Services
from dotenv import load_dotenv
load_dotenv()
AWS_KEY = os.getenv("AWSACCESS_KEY")
AWSECRET_KEY = os.getenv("AWSACCESS_KEY")

# os.environ["A_KEY"] = API_KEY


# s3 = boto3.resource('s3', aws_access_key_id=AWS_KEY,
#          aws_secret_access_key= AWSECRET_KEY)
# s3_client = boto3.client('s3')
s3_client = boto3.client('s3')
HOME = os.path.dirname(os.path.abspath(__file__))
# sns = boto3.client('sns')

#CREDIT MODEL and SCALER MODEL
customer_bucket = 'chat-customers'
# customer_data = 'data.txt'
userID = 'dfgh-gfjfjk-hjdkk-jdjdjs'
user_name = 'Akin'
customer_data = userID +'_' + user_name +'/dataset/data.txt'

local_file_name = HOME +'/'+ userID +'_' + user_name +'/data.txt'
# s3.Bucket(customer_bucket).download_file(customer_data, local_file_name)
# s3.Bucket(customer_bucket).upload_file(local_file_name, customer_data)
# /Users/mac/Desktop/projects/JacobRyanMedia/data.txt
# os.makedirs('/tmp/'+userID +'_' + user_name +'/unprocessed/', exist_ok=True)
# s3_client.download_file(customer_bucket, customer_data, local_file_name)
# s3_client.upload_file(local_file_name, customer_bucket, customer_data)

def upload_folder_to_s3(local_folder_path, bucket_name, s3_folder_name):
    # Initialize the S3 client
    s3_client = boto3.client('s3')

    for root, dirs, files in os.walk(local_folder_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            s3_object_key = os.path.relpath(local_file_path, local_folder_path)
            s3_object_key = os.path.join(s3_folder_name, s3_object_key)

            try:
                # Upload each file to S3
                s3_client.upload_file(local_file_path, bucket_name, s3_object_key)
                print(f"Uploaded {local_file_path} to S3 as {s3_object_key}")
            except Exception as e:
                print(f"Error uploading {local_file_path} to S3:", e)

def download_folder_from_s3(bucket_name, s3_folder_name, local_folder_path):
    # Initialize the S3 client
    s3_client = boto3.client('s3')

    try:
        # List objects in the S3 folder
        objects = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_folder_name)

        for obj in objects.get('Contents', []):
            s3_object_key = obj['Key']
            local_file_path = os.path.join(local_folder_path, os.path.relpath(s3_object_key, s3_folder_name))

            try:
                # Create directories if they don't exist
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                # Download each file from S3
                s3_client.download_file(bucket_name, s3_object_key, local_file_path)
                print(f"Downloaded {s3_object_key} from S3 to {local_file_path}")
            except Exception as e:
                print(f"Error downloading {s3_object_key} from S3:", e)
    except Exception as e:
        print("Error listing objects in S3:", e)
