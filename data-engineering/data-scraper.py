import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to get the MVP data for a specific year
def get_mvp_data(year):
    url = f'https://www.basketball-reference.com/awards/awards_{year}.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the MVP table
    mvp_table = soup.find('table', {'id': 'mvp'})
    
    if not mvp_table:
        print(f'No MVP table found for {year}')
        return []
    
    # Extract the headers
    headers = [th.getText() for th in mvp_table.find_all('th', {'scope': 'col'})][1:]  # Exclude the rank column
    
    # Extract the rows of the table
    rows = mvp_table.find('tbody').find_all('tr', limit=10)  # Limit to top 10
    
    data = []
    for row in rows:
        stats = [td.getText() for td in row.find_all('td')]
        if stats:
            data.append(stats)
    
    return data, headers

# Function to scrape MVP data for a range of years and save to CSV
def scrape_mvp_data(start_year, end_year, output_file='mvp_stats.csv'):
    all_data = []
    for year in range(start_year, end_year + 1):
        data, headers = get_mvp_data(year)
        for row in data:
            row.insert(0, year)  # Add the year at the start of each row
            all_data.append(row)
    
    # Create a DataFrame and save it as a CSV
    df = pd.DataFrame(all_data, columns=['Year'] + headers)
    df.to_csv(output_file, index=False)
    print(f'Data saved to {output_file}')

# Scrape data for a range of years
scrape_mvp_data(2000, 2023)
