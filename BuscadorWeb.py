import urllib.parse
from duckduckgo_search import DDGS

def pesquisar_na_web_externa(termo):
    """
    Realiza uma busca na internet usando DuckDuckGo.
    Retorna o título, resumo e link do primeiro resultado.
    """
    try:
        with DDGS() as ddg:
            results = ddg.text(keywords=termo, region="pt-br", max_results=1)
            
            if results:
                primeiro_resultado = results[0]
                titulo = primeiro_resultado.get('title', 'Título não disponível')
                resumo = primeiro_resultado.get('body', 'Nenhuma descrição disponível.') # Pega o resumo ou uma mensagem padrão
                link = primeiro_resultado.get('href', '#')
                
                return f"Título: {titulo}\n\nResumo: {resumo}\n\n", link
            else:
                return "Nenhum resultado encontrado na pesquisa externa.", ""
    except Exception as e:
        return f"Erro na pesquisa na web: {e}", ""

if __name__ == "__main__":
    resultado, link = pesquisar_na_web_externa("inteligencia artificial")
    print(resultado)
    print(f"Link: {link}")