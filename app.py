import streamlit as st
from azure.data.tables import TableServiceClient
import os
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Load environment variables
from dotenv import load_dotenv
load_dotenv()
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

# Initialize Table Service Client
if connect_str:
    table_service = TableServiceClient.from_connection_string(connect_str)
    table_client = table_service.get_table_client(table_name="DeviceTest01")
else:
    raise ValueError("Connection string is not set.")

def parse_date_from_description(description):
    """Extracts the date from the description assuming the format 'Date: MM/DD, YYYY ...'"""
    try:
        # Assumption: description starts with 'Date: MM/DD, YYYY'
        # For example, 'Date: 04/30, 2024 Pest control needed'
        date_str = description.split('Date: ')[1].split(',')[0].strip()  # Adjust to capture the year correctly
        print("Debug - Extracted date string:", date_str)  # Debugging output
        return datetime.strptime(date_str, '%m/%d, %Y').date()
    except Exception as e:
        print(f"Failed to parse date: {str(e)}")
        return None


def get_images_for_date(selected_date):
    """Fetches entries from Azure Table Storage for a specific date"""
    try:
        images = []
        entities = table_client.list_entities()
        for entity in entities:
            print("Debug - Description being processed:", entity['Description']) 
            entity_date = parse_date_from_description(entity['Description'])
            if entity_date == selected_date:
                images.append(entity)
        return images
    except Exception as e:
        st.error(f"Failed to fetch data: {str(e)}")
        return []
    

def display_images(images):
    """ Displays images and their metadata """
    if images:
        for image in images:
            st.image(image['ImageUrl'], caption=f"{image['FileName']} - {image['Description']}")
    else:
        st.write("No images found for this date.")

def main():
    st.title('Image Viewer App')
    st.write("Select a date to view images:")
    date = st.date_input("Pick a date")
    if date:
        images = get_images_for_date(date)
        display_images(images)

if __name__ == "__main__":
    main()