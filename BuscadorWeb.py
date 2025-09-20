import urllib.parse
from duckduckgo_search import DDGS

# Novo: Lista de sites para pesquisa, em ordem de prioridade
sites_prioritarios = [
    "lupa.uol.com.br",
    "firstdraftnews.org",
    "g1.globo.com"
]

def pesquisar_na_web_externa(termo):
    """
    Realiza uma busca na internet em sites específicos com prioridade.
    """
    try:
        with DDGS() as ddg:
            # Novo: Loop para buscar em cada site prioritário
            for site in sites_prioritarios:
                # Constrói a query com o operador "site:"
                query = f"{termo} site:{site}"
                results = ddg.text(keywords=query, region="pt-br", max_results=1)

                if results:
                    primeiro_resultado = results[0]
                    titulo = primeiro_resultado.get('title', 'Título não disponível')
                    resumo = primeiro_resultado.get('body', 'Nenhuma descrição disponível.')
                    link = primeiro_resultado.get('href', '#')

                    # Retorna o primeiro resultado encontrado e para a busca
                    return f"Título: {titulo}\n\nResumo: {resumo}\n\n", link

            # Se o loop terminar sem encontrar nenhum resultado
            return "Nenhum resultado encontrado nos sites prioritários.", ""

    except Exception as e:
        return f"Erro na pesquisa na web: {e}", ""


if __name__ == "__main__":
    resultado, link = pesquisar_na_web_externa("inteligencia artificial")
    print(resultado)
    print(f"Link: {link}")