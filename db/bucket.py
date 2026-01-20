import os
from boto3.session import Session
from botocore.config import Config
from botocore.exceptions import ClientError
from datetime import datetime
import uuid
import asyncio

ACCESS_KEY = 'DO00JANRUDDDK46JFLPR'
SECRET_KEY = 'C1djMNFJGN3p8aLDakZ1a349oyEU3Jv/wmYglXGX0o4'
SPACE_NAME = 'oyster-bucket' 
REGION = 'sgp1'

session = Session()
client = session.client(
    's3',
    endpoint_url=f'https://{REGION}.digitaloceanspaces.com',
    config=Config(s3={'addressing_style': 'virtual'}),
    region_name=REGION,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

class BucketStorageStructure:
    STRUCTURE = {
        '理貨單' : {},
        '宅配貼紙' : {},
        '明細表': {},
    }

    @staticmethod
    def create_structure(base_path, bucket_name=SPACE_NAME):
        """
        Create folder structure from template
        """
        
        def create_folders(structure, current_path=''):
            folders = []
            for key, value in structure.items():
                folder_path = f'{current_path}{key}/'
                folders.append(folder_path)
                
                if isinstance(value, dict) and value:
                    # Recursively create subfolders
                    folders.extend(create_folders(value, folder_path))
            
            return folders
        
        # Generate all folder paths
        base = f'{base_path}/'
        all_folders = [base + f for f in create_folders(BucketStorageStructure.STRUCTURE)]
        
        # Create all folders
        for folder in all_folders:
            try:
                client.put_object(
                    Bucket=SPACE_NAME,
                    Key=folder,
                    Body=b''
                )
                print(f'Created: {folder}')
            except Exception as e:
                print(f'Error: {e}')
        
        return all_folders

def folder_exists_spaces(folder_path, client=client):
    """
    Check if a folder exists in DigitalOcean Spaces
    
    Args:
        space_name: Name of the Space
        folder_path: Path to folder (should end with '/')
        region: Region of the Space
        
    Returns:
        True if folder exists, False otherwise
    """
    # Ensure folder_path ends with '/'
    if not folder_path.endswith('/'):
        folder_path += '/'
    
    try:
        response = client.list_objects_v2(
            Bucket=SPACE_NAME,
            Prefix=folder_path,
            MaxKeys=1
        )
        
        return 'Contents' in response
        
    except Exception as e:
        print(f"Error checking folder: {e}")
        return False

def file_exists_spaces(file_path, client=client):
    """
    Check if a file exists in DigitalOcean Spaces
    
    Args:
        space_name: Name of the Space
        file_path: Path to file
        region: Region of the Space
        
    Returns:
        True if file exists, False otherwise
    """
    try:
        client.head_object(Bucket=SPACE_NAME, Key=file_path)
        print('File exists')
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            print(f"Error checking file: {e}")
            raise


async def create_folder(folder, client=client):
    # Create the folder by uploading a zero-sized object with a trailing slash
    # This makes it visible in the DO control panel
    folder_key = folder.rstrip('/') + '/'

    try:
        client.put_object(Bucket=SPACE_NAME, Key=folder_key, Body=b'')
        print(f"Folder '{folder}' (as key '{folder_key}') created successfully in Space '{SPACE_NAME}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

async def upload_file(file_name, object_name=None, ):
    if object_name is None:
        object_name = os.path.basename(file_name)
    try:
        client.upload_file(file_name, SPACE_NAME, object_name)
        print(f"File '{object_name}' has been successfully uploaded in Space '{SPACE_NAME}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

async def create_folder_structure_if_not_exist(date):
    folder = date.strftime('%Y-%m')
    # folder = '2026-02'
    if ~folder_exists_spaces(folder_path=folder) : 
        folder_structure = BucketStorageStructure.create_structure(
            folder
        )

async def download_pdf_from_bucket(s3_object_key, local_file_path, client=client):
    """
    Downloads a file from an S3 bucket to a local path.
    """
    try:
        # Ensure the local directory exists
        local_dir = os.path.dirname(local_file_path)
        if local_dir and not os.path.exists(local_dir):
            os.makedirs(local_dir)

        
        if file_exists_spaces(s3_object_key):
            # Download the file
            client.download_file(SPACE_NAME, s3_object_key, local_file_path)
        print(f"✅ Successfully downloaded '{s3_object_key}' to '{local_file_path}'")

    except Exception as e:
        print(f"❌ Error downloading file: {e}")


if __name__ == '__main__':
    # asyncio.run(create_folder('2026-01'))
    # print(datetime.now().strftime('%Y-%m'))
    # print(folder_exists_spaces(folder_path='2026-02', space_name='oyster-bucket'))
    # print(file_exists_spaces('2026-01/理貨單/O25004172010_理貨單.pdf'))
    asyncio.run(download_pdf_from_bucket(s3_object_key='2026-01/理貨單/O25004172010_理貨單.pdf', local_file_path=f'{uuid.uuid4()}.pdf'))