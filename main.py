import streamlit as st
from azure.data.tables import TableServiceClient
import os
from datetime import datetime
import urllib3
urllib3.disable_warnings()

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

def setup_table_client(connect_str, table_name):
    """Setup and return a table client using the given connection string and table name."""
    if not connect_str:
        raise ValueError("Connection string is not set.")
    table_service = TableServiceClient.from_connection_string(connect_str)
    table_client = table_service.get_table_client(table_name=table_name)
    
    try:
        table_client.create_table()  # Try to create the table, if it doesn't exist.
        print("Table created or already exists.")
    except Exception as e:
        print(f"Failed to create table: {str(e)}")  # Handle errors in table creation.
    
    return table_client

def get_images_for_date(selected_date, table_client):
    """Fetches entries from Azure Table Storage for a specific date stored in 'DT'."""
    try:
        images = []
        entities = table_client.list_entities()
        
        for entity in entities:
            # Use the 'DT' field for the date comparison
            entity_datetime = datetime.fromisoformat(entity['DT'].rstrip('Z'))
            if entity_datetime.date() == selected_date:
                images.append(entity)
        return images
    except Exception as e:
        st.error(f"Failed to fetch data: {str(e)}")
        return []

def display_images(images):
    """Displays images and their metadata."""
    if not images:
        st.write("No images found for this date.")
        return
    for image in images:
        # Remove 'Z' before converting to datetime object if it's there
        dt = datetime.fromisoformat(image['DT'].rstrip('Z'))
        # Format datetime object to string for display
        formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
        caption = f"{image['FileName']} - {image['Description']} - {formatted_date}"
        st.image(image['ImageUrl'], caption=caption)
    
def main():
    st.title('Pest Viewer App')
    st.write("Select a date to view images:")
    date = st.date_input("Pick a date")
    
    if date:
        table_client = setup_table_client(connect_str, "DeviceTest01")
        images = get_images_for_date(date, table_client)
        display_images(images)

if __name__ == "__main__":
    main()
