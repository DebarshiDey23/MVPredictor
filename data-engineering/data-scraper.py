import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.preprocessing import LabelEncoder, StandardScaler
import re

# Function to get MVP data for a specific year
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

# Function to get player biography (e.g., birthplace)
def get_player_bio(player_url):
    response = requests.get(f'https://www.basketball-reference.com{player_url}')
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Safely locate the meta div
    meta_div = soup.find('div', {'id': 'meta'})
    if not meta_div:
        print(f"Meta div not found for {player_url}")
        return None  # Or you could return 0 or some other default value
    
    # Try to find birth information
    birth_info = meta_div.find('p')
    if not birth_info:
        print(f"Birth information not found for {player_url}")
        return None
    
    birth_info_text = birth_info.getText()
    
    # Determine if born in America
    born_in_america = 1 if 'USA' in birth_info_text else 0
    
    return born_in_america


# Function to get team standings for a given year
def get_team_standings(year):
    url = f'https://www.basketball-reference.com/leagues/NBA_{year}_standings.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    standings = {}
    
    # Extract the standings tables for both conferences
    for conference in ['divs_standings_E', 'divs_standings_W']:
        table = soup.find('table', {'id': conference})
        if table is None:
            print(f"No standings table found for conference {conference} in {year}")
            continue
        
        for row in table.find('tbody').find_all('tr'):
            # Skip rows without a team link
            if row.find('a') is None:
                continue
            
            team_name = row.find('a').getText()
            wins = row.find_all('td')[1].getText()

            try:
                # Check if the rank is present
                rank_span = row.find('span')
                rank = int(rank_span.getText()) if rank_span else None
            except ValueError:
                rank = None

            try:
                # Convert wins to an integer if possible
                wins = int(wins)
            except ValueError:
                wins = None
            
            standings[team_name] = (rank, wins)
    
    return standings


# Function to scrape MVP data for a range of years and save to CSV
def scrape_mvp_data(start_year, end_year, output_file='mvp_stats.csv'):
    all_data = []
    mvp_counts = {}  # Track MVP wins
    
    for year in range(start_year, end_year + 1):
        data, headers = get_mvp_data(year)
        standings = get_team_standings(year)
        
        for row in data:
            player_name = row[0]
            player_url = row[0].replace(' ', '_').lower() + '.html'
            team_name = row[1]
            
            # Calculate MVP count up until that season
            if player_name in mvp_counts:
                mvp_count = mvp_counts[player_name]
            else:
                mvp_count = 0
            
            # Increment MVP count for this player
            mvp_counts[player_name] = mvp_count + 1
            
            # Get the player's birthplace info
            born_in_america = get_player_bio(f'/players/{player_url}')
            
            # Get team standings data
            if team_name in standings:
                team_rank, team_wins = standings[team_name]
            else:
                team_rank, team_wins = None, None
            
            # Add additional statistics to row
            row.extend([mvp_count, team_rank, team_wins, born_in_america])
            all_data.append(row)
    
    # Update headers
    headers.extend(['MVP_Count_Until_Season', 'Team_Conference_Rank', 'Team_Wins', 'Born_in_America'])
    
    # Create a DataFrame and save it as a CSV
    df = pd.DataFrame(all_data, columns=['Year'] + headers)
    df.to_csv(output_file, index=False)
    print(f'Data saved to {output_file}')

# Function to impute missing values using KNN
def impute_missing_values(file_name):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_name)

    # Encode categorical columns (like player names) to numerical values
    encoder = LabelEncoder()
    df['Player'] = encoder.fit_transform(df['Player'])

    # Normalize the data to improve KNN performance
    scaler = StandardScaler()
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_columns] = scaler.fit_transform(df[numeric_columns])

    # Apply KNN imputer to fill missing values
    imputer = KNNImputer(n_neighbors=5)
    df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)

    # Convert any columns back to their original scale if needed
    df_imputed[numeric_columns] = scaler.inverse_transform(df_imputed[numeric_columns])

    # Decode the player names back to their original labels
    df_imputed['Player'] = encoder.inverse_transform(df_imputed['Player'].astype(int))

    # Save the imputed DataFrame back to a CSV file
    df_imputed.to_csv('mvp_stats_imputed.csv', index=False)
    print("Imputed data saved to mvp_stats_imputed.csv")

# Main execution
if __name__ == "__main__":
    # Step 1: Scrape the data
    scrape_mvp_data(2000, 2023)
    
    # Step 2: Impute missing values
    impute_missing_values('mvp_stats.csv')
