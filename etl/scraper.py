from bs4 import BeautifulSoup
import requests
import time
import csv
import boto3
import logging
from io import StringIO

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def extract_listings(soup):
    listings = soup.find_all('article')
    all_listing_details = []

    for listing in listings:
        # Extracting description
        description = listing.find('h3').a.get('title')

        # Extracting price
        price = listing.find('li', class_='propertyPrice').span.get_text()
        link = listing.find('h3').a.get('href')

        # Extracting location
        location = listing.find('span', itemprop='addressLocality').get_text()

        # Extracting area, number of rooms, bathrooms, and parking spaces
        area = next((li.get_text().strip() for li in listing.find_all('li') if 'icon-agency_area02' in str(li)), None)
        number_of_rooms = next((li.get_text().strip() for li in listing.find_all('li') if 'icon-agency_bed02' in str(li)), None)
        number_of_bathrooms = next((li.get_text().strip() for li in listing.find_all('li') if 'icon-agency_bath02' in str(li)), None)
        parking_spaces = next((li.get_text().strip() for li in listing.find_all('li') if 'icon-agency_garage02' in str(li)), None)

        listing_details = {
            'description': description,
            'price': price,
            'location': location,
            'area': area,
            'number_of_rooms': number_of_rooms,
            'number_of_bathrooms': number_of_bathrooms,
            'parking_spaces': parking_spaces,
            'link': link
        }

        all_listing_details.append(listing_details)

    return all_listing_details

def get_next_page_url(soup, base_url):
    # Find the 'next page' link and return its URL if it exists
    next_page = soup.find('a', class_='nextPage')
    return next_page['href'] if next_page else None

def scrape_all_pages(base_url):
    all_data = []
    while True:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        all_data.extend(extract_listings(soup))

        next_page_url = get_next_page_url(soup, base_url)
        if not next_page_url:
            break

        base_url = "https://www.athome.lu" + next_page_url
        time.sleep(1) # Sleep to prevent overwhelming the server

    logger.info("The scraping is done")
    return all_data

def handler(event, context):
    base_url = 'https://www.athome.lu/srp/?tr=rent&q=faee1a4a&loc=L2-luxembourg&ptypes=flat'
    all_data = scrape_all_pages(base_url)

    # Save to CSV in memory
    csv_buffer = StringIO()
    csv_writer = csv.DictWriter(csv_buffer, fieldnames=all_data[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(all_data)
    csv_buffer.seek(0)

    # Save to S3
    s3 = boto3.resource('s3')
    s3.Bucket("housing-lu-omar").put_object(Key="listings.csv", Body=csv_buffer.getvalue().encode('utf-8'))

    return {
        'statusCode': 200,
        'body': 'File saved successfully'
    }
