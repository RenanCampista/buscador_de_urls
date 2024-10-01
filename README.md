# buscador_de_urls
Este script busca as urls de um arquivo de postagens do facebook ou instagram e as salva em um arquivo .csv


## Como usar
1. Clone o repositório
2. Instale as dependências
```bash
pip install -r requirements.txt
```
3. Execute o script
```bash
python buscador_de_urls.py
```
4. Siga as instruções do script

## Observações
- O arquivo de postagens deve estar no formato .csv.
- O script faz a busca de urls através de requisições http, usando bing, duckduckgo e google. O google pode bloquear o acesso se muitas requisições forem feitas em um curto espaço de tempo. Nesse caso, o script irá suspender a utilização do google por um tempo e continuar a busca com os outros motores de busca.