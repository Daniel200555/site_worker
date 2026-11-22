
import boto3
import json
from log import *
from botocore.exceptions import ClientError
from read_env import ReadEnv

class S3Client:

    def __init__(self):
        self.read_env = ReadEnv()
        self.s3_client = boto3.client("s3", endpoint_url=self.read_env.s3_endpoint_url, aws_access_key_id=self.read_env.s3_access_key_id, aws_secret_access_key=self.read_env.s3_secret_access_key)

    def create_rewrite_list(self, site_name: str, list_name: str, data: list[dict]) -> None:
        try:
            print_log("S3_CLIENT", "CREATE_REWRITE_LIST", f"Start to create or rewrite for list -> {list_name} in site -> {site_name}")
            self.s3_client.put_object(Bucket=self.read_env.s3_bucket_name, Key=f"{site_name}/{list_name}.json", Body=json.dumps(data, ensure_ascii=False, indent=4).encode("utf-8"), ContentType="application/json")
            print_success_log("S3_CLIENT", "CREATE_REWRITE_LIST", f"List {list_name} in site {site_name} created or upgrated")
        except ClientError as e:
            print_error_log("S3_CLIENT", "CREATE_REWRITE_LIST", f"S3 create or rewrite list for site -> {site_name} and list -> {list_name}, \n ERROR: {e.response}")
            raise

    def delete_list(self, site_name: str, list_name: str):
        try:
            print_log("S3_CLIENT", "DELETE_LIST", f"Start to delete list -> {list_name} in site -> {site_name}")
            self.s3_client.delete_object(Bucket=self.read_env.s3_bucket_name, Key=f"{site_name}/{list_name}.json")
            print_success_log("S3_CLIENT", "DELETE_LIST", f"S3 list -> {list_name} in site -> {site_name} deleted")
        except ClientError as e:
            print_error_log("S3_CLIENT", "DELETE_LIST", f"S3 delete list -> {list_name} in site -> {site_name}, \n ERROR: {e.response}")
            raise

    def get_file(self, key: str) -> dict:
        response = self.s3_client.get_object(Bucket=self.read_env.s3_bucket_name,Key=key)
        return json.loads(response["Body"].read().decode("utf-8"))