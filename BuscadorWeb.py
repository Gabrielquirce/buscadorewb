# buscadorweb.py
import urllib.parse
from duckduckgo_search import DDGS

def pesquisar_na_web_externa(termo, dominio=None):
    """
    Realiza uma busca na internet usando DuckDuckGo, opcionalmente em um domínio específico,
    priorizando resultados em português brasileiro.
    Retorna o título, resumo e link do primeiro resultado.
    """
    try:
        keywords = termo
        if dominio:
            keywords = f"{termo} site:{dominio}"

        with DDGS() as ddg:
            # O parâmetro region='pt-br' direciona a busca para resultados brasileiros
            results = ddg.text(keywords=keywords, region="pt-br", max_results=1)
            
            if results:
                primeiro_resultado = results[0]
                titulo = primeiro_resultado.get('title', 'Título não disponível')
                resumo = primeiro_resultado.get('body', 'Nenhuma descrição disponível.')
                link = primeiro_resultado.get('href', '#')
                
                return f"Título: {titulo}\n\nResumo: {resumo}\n\n", link
            else:
                return "Nenhum resultado encontrado na pesquisa externa.", ""
    except Exception as e:
        return f"Erro na pesquisa na web: {e}", ""

if __name__ == "__main__":
    resultado, link = pesquisar_na_web_externa("inteligencia artificial", "g1.globo.com")
    print(resultado)
    print(f"Link: {link}")