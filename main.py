"""Busca URLs de posts no Google a partir de um arquivo CSV com posts."""

from enum import Enum
import sys
import os
import re
import time
import random
from urllib.parse import urlparse
import pandas as pd
import requests
from bs4 import BeautifulSoup

MIN_TEXT_LENGTH = 200
MAX_TEXT_LENGTH = 3500

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.48",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

SEARCH_ENGINES = [
    f"https://www.google.com/search?q=",
    f"https://duckduckgo.com/html/?q=",
    f"https://www.bing.com/search?q=",
    f"https://search.yahoo.com/search?p=",
    f"https://www.ask.com/web?q="
]


class SocialNetwork(Enum):
    """The social networks for which the URLs are extracted."""
    FACEBOOK = ("Caption", "site: facebook.com", "https://www.facebook.com/", "URL", ["posts", "videos", "photos", "groups"])
    INSTAGRAM = ("Caption", "site: instagram.com", "https://www.instagram.com/", "URL", ["p/", "tv/", "reel/", "video/", "photo/"])
    
    def get_text_column(self) -> str:
        return self.value[0]
    
    def get_url_query(self) -> str:
        return self.value[1]
    
    def get_post_url(self) -> str:
        return self.value[2]
    
    def get_url_column(self) -> str:
        return self.value[3]
    
    def get_valid_substrings(self) -> list:
        return self.value[4]
    

def select_social_network(sn: int) -> SocialNetwork:
    """Select the social network based on user input."""
    if sn == 1:
        return SocialNetwork.FACEBOOK
    elif sn == 2:
        return SocialNetwork.INSTAGRAM
    else:
        print("Escolha inválida. Tente novamente.")
        sys.exit(1)


def validate_file_extension(file_name: str, extension: str):
    """Check if the file has the correct extension."""
    if not file_name.endswith(extension):
        print(f"Arquivo inválido. O arquivo deve ser um {extension}")
        sys.exit(1) 


def list_files_and_get_input() -> str:
    """List files and get user input for file selection."""
    files = [file for file in os.listdir('.') if os.path.isfile(file) and not file.startswith('.')]
    while True:
        user_input = input('Please enter the file name ("?" to list): ')
        if user_input == '?':
            for i, file in enumerate(files, 1):
                print(f"{i}. {file}")
        elif user_input.isdigit():
            file_index = int(user_input) - 1
            if 0 <= file_index < len(files):
                return files[file_index]
            else:
                print("Invalid number. Please try again.")      
        else:
            if user_input in files:
                return user_input
            else:
                print("Invalid file name. Please try again.")


def read_posts_from_extraction(file_path: str, social_network: SocialNetwork) -> pd.DataFrame:
    """Reads the CSV file with the posts and returns a DataFrame."""
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {file_path}")
        sys.exit(1)
    except pd.errors.ParserError:
        print(f"Erro ao ler o arquivo: {file_path}")
        sys.exit(1)
    except KeyError as e:
        print(f"Coluna não encontrada: {e}")
        sys.exit(1)


def filter_bmp_characters(text: str) -> str:
    """Remove characters outside the Basic Multilingual Plane (BMP)."""
    return re.sub(r'[^\u0000-\uFFFF]', '', text)


def search_with_requests(query: str, social_network: SocialNetwork) -> str:
    """Performs a search using requests and BeautifulSoup and returns the first matching URL."""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
    }
    
    query_filtered = filter_bmp_characters(query)
    search_engines = [engine + query_filtered for engine in SEARCH_ENGINES]
    random.shuffle(search_engines) # Randomize the search order
    
    for search_url in search_engines:
        response = requests.get(
            url=search_url, 
            headers=headers
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            if social_network.get_post_url() in href and \
                any(substring in href for substring in social_network.get_valid_substrings()):
                return href
        time.sleep(random.uniform(1, 3)) 
    return ''


def extract_relevant_url(url: str) -> str:
    """Extracts the relevant part of the URL."""
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"


def main():
    social_network = select_social_network(int(input("Escolha a rede social:\n1 - Facebook\n2 - Instagram\n")))
    print("Selecione o arquivo de extração (CSV) com os posts:")
    file_name = list_files_and_get_input()
    validate_file_extension(file_name, '.csv')
    
    data_posts = read_posts_from_extraction(file_name, social_network)
    data_posts[social_network.get_url_column()] = ''
    
    search_success = 0
    for index, row in data_posts.iterrows():
        text = row[social_network.get_text_column()]
        query = f"{social_network.get_url_query()}+{text}"
        
        if not MIN_TEXT_LENGTH <= len(query) <= MAX_TEXT_LENGTH:
            print(f"Texto da linha {index + 1} ignorado (comprimento inválido: {len(query)} caracteres)")
            continue
        
        url = search_with_requests(query, social_network)
        relevant_url = extract_relevant_url(url) if url else ''
        data_posts.at[index, social_network.get_url_column()] = relevant_url
        
        if url:
            print(f"Post da linha {index + 1} encontrado: {relevant_url}")
            search_success += 1
        else:
            print(f"Post da linha {index + 1} não encontrado.")
        
        time.sleep(random.uniform(2, 5))
    
    print(f"Busca finalizada. URLs encontradas: {search_success}/{len(data_posts)}")
    data_posts.to_csv(f'{file_name[:-4]}_with_urls.csv', index=False)


if __name__ == '__main__':
    main()

