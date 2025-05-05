import os
import requests
from bs4 import BeautifulSoup
import re

# Main page URL containing links to individual updates
main_url = "https://www.fire.ca.gov/incidents/2025/1/23/border-2-fire/updates"

# Set a User-Agent to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Folder to save the text files
output_folder = 'Test_reports'

# Ensure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)


# Function to sanitize the file name (remove or replace invalid characters)
def sanitize_filename(file_name):
    # Replace invalid characters with an underscore (_)
    file_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)
    # Replace spaces with underscores
    file_name = file_name.replace(' ', '_')
    return file_name


# Function to scrape the details from a subpage and save to text file
def scrape_update_page(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve subpage {url}, status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Scrape the title, date, time, and status summary
    try:
        # Scrape fire name (second span inside the <h1>)
        title_section = soup.find('div', class_='col-lg')  # Find the <div> with the class 'col-lg'

        # Extract fire name
        fire_name = title_section.find('h1').find_all('span', class_='d-block fw-normal lh-1')[0].get_text(strip=True)

        # Extract date and time
        date_time_section = title_section.find('dl')  # <dl> tag containing date and time
        date = date_time_section.find('dd', class_='d-inline-block me-2').get_text(strip=True)
        time = date_time_section.find_all('dd', class_='d-inline-block')[-1].get_text(strip=True)

        # Scrape situation summary (assumed to be in the <p> after the <h3> with class 'h4 pb-2 border-bottom')
        situation_summary_section = soup.find('h3', class_='h4 pb-2 border-bottom')
        situation_summary = situation_summary_section.find_next('p').get_text(strip=True)

        # Prepare text content for saving
        content = f"{fire_name} as of {date} at {time}:"
        content += f"\n{situation_summary}"

        # Create a safe file name by sanitizing the file name
        file_name = f"Update_report_{fire_name}_{date.replace('/', '_')}_{time.replace(':', '_').replace(' ', '_').replace('PM', 'PM_').replace('AM', 'AM_')}.txt"
        file_name = sanitize_filename(file_name)  # Sanitize file name
        file_path = os.path.join(output_folder, file_name)  # Save to the specified folder

        # Save the content to a text file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        print(f"Saved update information for {fire_name} in {file_name}")

    except Exception as e:
        print(f"Error scraping subpage {url}: {e}")


# Function to scrape the main page and collect all the update links
def scrape_main_page():
    # Send HTTP request to get the main page content
    response = requests.get(main_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve main page, status code: {response.status_code}")
        return

    # Parse the HTML content of the main page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links to subpages (update pages)
    update_links = []
    for link in soup.find_all('a', href=True):
        # Extract links with the desired structure
        if "/incidents/" in link['href'] and "updates" in link['href']:
            full_url = "https://www.fire.ca.gov" + link['href']
            update_links.append(full_url)

    # Print the update links to check if they are collected correctly
    print(f"Found {len(update_links)} update links.")
    return update_links


# Scrape the main page to get update links
update_links = scrape_main_page()

# Scrape each update link and save to a text file
for link in update_links:
    scrape_update_page(link)



