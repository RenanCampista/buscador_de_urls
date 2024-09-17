
import pandas as pd
from enum import Enum
from googlesearch import search
import sys
import os
import re
import time

class SocialNetwork(Enum):
    """The social networks for which the URLs are extracted."""
    FACEBOOK = ("post_owner.username", "text", "site: facebook.com", "https://www.facebook.com/")
    INSTAGRAM = ("post_owner.username", "text", "site: instagram.com", "https://www.instagram.com/p/")
    
    def get_username_column(self) -> str:
        """Returns the username column name of the social network in the CSV file."""
        return self.value[0]
    
    def get_text_column(self) -> str:
        """Returns the post text column name of the social network in the CSV file."""
        return self.value[1]
    
    def get_url_query(self) -> str:
        """Returns the URL query of the social network."""
        return self.value[2]
    
    def get_post_url(self) -> str:
        """Returns the post URL of the social network."""
        return self.value[3]
    
    
def select_social_network(sn: int) -> SocialNetwork:
    """Returns the corresponding SocialNetwork enum based on user input."""
    if sn == 1:
        return SocialNetwork.FACEBOOK
    elif sn == 2:
        return SocialNetwork.INSTAGRAM
    else:
        print("Opção inválida")
        sys.exit(1)
        
        
def validate_file_extension(file_name: str, extension: str):
    """Validates the file extension."""
    if not file_name.endswith(extension):
        print(f"Arquivo inválido. O arquivo deve ser um {extension}")
        sys.exit(1) 
        

def list_files_and_get_input() -> str:
    """Lists the non-hidden files in the current directory and gets the user input for the file name by number."""
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
    """Reads the URLs from the extraction file and replaces newlines with spaces."""
    try:
        df = pd.read_csv(file_path)
        text_column = social_network.get_text_column()
        df[text_column].apply(lambda x: re.sub(r'\n', ' ', x)).tolist()
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {file_path}")
        sys.exit(1)
    except pd.errors.ParserError:
        print(f"Erro ao ler o arquivo: {file_path}")
        sys.exit(1)
    except KeyError:
        print(f"Coluna não encontrada: {social_network.get_post_url_csv()}")
        sys.exit(1)
    return df


if __name__ == '__main__':
    
    social_network = select_social_network(int(input("Escolha a rede social:\n1 - Facebook\n2 - Instagram\n")))
    
    print("Selecione o arquivo de extração (CSV) com os posts:")
    file_name = list_files_and_get_input()
    validate_file_extension(file_name, '.csv')
    
    data_posts = read_posts_from_extraction(file_name, social_network)
    data_posts['url'] = ''

    print("Procurando URLs dos posts...")
    for index, row in data_posts.iterrows():
        text = row[social_network.get_text_column()]
        query = f"{social_network.get_url_query()} {text}"
        if len(query) > 2048: continue
        for url in search(query, lang="pt", region="BR"):
            if social_network.get_post_url() in url:
                data_posts.at[index, 'url'] = url
                break
        time.sleep(2)

    data_posts.to_csv('posts_with_urls.csv', index=False)