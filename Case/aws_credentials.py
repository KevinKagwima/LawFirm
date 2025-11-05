from dotenv import load_dotenv
import os

load_dotenv(override=True)

class awsCredentials:
  aws_access_key = os.environ.get("aws_access_key")
  aws_secret_key = os.environ.get("aws_secret_key")
  bucket_name = os.environ.get("bucket_name")
  region = os.environ.get("region")