import requests
import urllib.parse
from bs4 import BeautifulSoup

def get_full_text_formatted(termo):
    """
    Obtém o texto completo de um artigo da Wikipédia e o formata como uma string.
    Retorna uma tupla (sucesso, texto_ou_erro).
    """
    termo_codificado = urllib.parse.quote(termo)
    url = f"https://pt.wikipedia.org/api/rest_v1/page/html/{termo_codificado}"
    
    headers = {
        "User-Agent": "MeuAplicativoDePesquisa/1.0"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove tags irrelevantes
        for tag in soup.find_all(['sup', 'table', 'aside', 'span', 'figure']):
            tag.extract()
            
        full_text = ""
        body = soup.find('body')
        if not body:
            return False, "Corpo do HTML não encontrado."

        for element in body.find_all(['p', 'h2', 'h3', 'h4', 'ul', 'ol', 'li']):
            if element.name == 'p':
                text = element.get_text(strip=True)
                if text:
                    full_text += text + '\n\n'
            elif element.name in ['h2', 'h3', 'h4']:
                text = element.get_text(strip=True)
                if text:
                    full_text += f"## {text}\n\n"
            elif element.name in ['ul', 'ol']:
                for item in element.find_all('li'):
                    text = item.get_text(strip=True)
                    if text:
                        full_text += '  • ' + text + '\n'
                full_text += '\n'

        return True, full_text
        
    except requests.exceptions.RequestException as e:
        return False, f"Erro ao obter texto completo: {e}\n"
    except Exception as e:
        return False, f"Ocorreu um erro inesperado ao processar o texto: {e}\n"

def pesquisar_wikipedia(termo, limite=3, tipo="resumo"):
    """
    Realiza uma busca na API da Wikipédia e retorna um resumo.
    """
    termo_codificado = urllib.parse.quote(termo)
    url = "https://pt.wikipedia.org/api/rest_v1/page/summary/" + termo_codificado
    
    headers = {
        "User-Agent": "MeuAplicativoDePesquisa/1.0"
    }

    try:
        resposta = requests.get(url, headers=headers)
        dados = resposta.json()
        
        if resposta.status_code == 404:
            return "Página '{termo}' não encontrada na Wikipédia.", "404"

        if resposta.status_code == 200:
            if "extract" in dados:
                resumo = dados["extract"]
                link = dados["content_urls"]["desktop"]["page"]

                if tipo == "palavras":
                    partes = resumo.split()
                    resumo_limitado = " ".join(partes[:limite])
                    if len(partes) > limite:
                        resumo_limitado += "..."
                elif tipo == "resumo":
                    resumo_limitado = resumo

                return resumo_limitado, link
            else:
                return "Não foi possível encontrar um resumo para este termo.", ""
        
        else:
            return f"Erro {resposta.status_code}: Não foi possível acessar a Wikipédia.", ""
    except requests.exceptions.RequestException as e:
        return f"Ocorreu um erro de conexão: {e}", ""
    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}", ""
        
def sugerir_titulos_wikipedia(termo):
    """
    Retorna sugestões de títulos da Wikipédia.
    """
    url = f"https://pt.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(termo)}&limit=10&format=json"
    try:
        response = requests.get(url, timeout=1)
        response.raise_for_status()
        dados = response.json()
        return dados[1]
    except (requests.exceptions.RequestException, IndexError):
        return []