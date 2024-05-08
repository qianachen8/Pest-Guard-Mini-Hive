from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient
from datetime import datetime
import os


# Initialize the BlobServiceClient
connect_str = 'DefaultEndpointsProtocol=https;AccountName=farmgazerpest;AccountKey=LPppF+JLCaiqTzd9J2Nb3IC+Sq58slLIatrs0P1ev7kUt0E5TohMjGPffghQ2rNoBghh0+fCv6fc+ASt/M+h1Q==;EndpointSuffix=core.windows.net'
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = 'pestimage'  # Specify your container name

container_client = blob_service_client.get_container_client(container_name)

def setup_container():
    try:
        container_client.create_container()
        print("Container created.")
    except Exception as e:
        if 'ContainerAlreadyExists' not in str(e):
            print("Unexpected error when creating container:", e)
        else:
            print("Container already exists.")



def setup_table_client():
    table_service = TableServiceClient.from_connection_string(connect_str)
    table_name = 'DeviceTest01'
    table_client = table_service.get_table_client(table_name)

    try:
        table_client.create_table()
        print("Table created or already exists.")
    except Exception as e:
        if 'TableAlreadyExists' not in str(e):
            print("Unexpected error:", e)
        else:
            print("Table check completed - already exists.")
    return table_client  # This line ensures that the table_client is returned after being set up

table_client = setup_table_client()

# Function to upload a file to Azure Blob Storage and store metadata in Azure Table Storage
def upload_file_and_save_metadata(file_path, description):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=os.path.basename(file_path))

    # Upload the image
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    # Get the blob URL
    blob_url = blob_client.url

    # Current timestamp in ISO 8601 format
    timestamp = datetime.utcnow().isoformat() + 'Z'

    # Insert or merge the new entity into the table
    metadata = {
        'PartitionKey': 'ImageDescription',  # Use a suitable partition key for your scenario
        'RowKey': os.path.basename(file_path),  # Unique identifier for the row (filename used here)
        'Description': description,
        'ImageUrl': blob_url,
        'FileName': os.path.basename(file_path),  # Storing the file name as well
        'Timestamp': timestamp,  # Storing the upload timestamp
        'DT': timestamp
    }
    table_client.upsert_entity(entity=metadata)

    return blob_url, metadata

if __name__ == "__main__":
    setup_container()
    image_path = '/Users/qinghongchen/Desktop/image 154.png'
    image_description = 'Date: 04/30, 2024\nPest category: Weevil\nNumber: 3\nAdvice: Call us to get more help'
    url, metadata = upload_file_and_save_metadata(image_path, image_description)
    print("Image URL:", url)
    print("Metadata stored:", metadata)

