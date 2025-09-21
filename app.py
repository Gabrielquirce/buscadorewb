# app.py

from flask import Flask, render_template, request, jsonify
from BuscadorWeb import pesquisar_na_web_externa
from buscadorwiki import pesquisar_wikipedia, get_full_text_formatted
import urllib.parse

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_api():
    data = request.json
    termo = data.get('query')
    source = data.get('source')
    search_type = data.get('type')

    if not termo:
        return jsonify({"error": "Por favor, digite um termo para pesquisar."}), 400

    if source == "wikipedia":
        if search_type == "tudo":
            # Chamada da função modificada que retorna a string
            success, full_text = get_full_text_formatted(termo)
            
            if not success:
                return jsonify({"error": full_text}), 500

            link = f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(termo)}"
            
            return jsonify({
                "full_text": full_text,
                "link": link,
                "source": "wikipedia"
            })
        else: # Tipo "resumo"
            resumo, link = pesquisar_wikipedia(termo, tipo="resumo")
            if link == "404":
                return jsonify({"summary": f"Página '{termo}' não encontrada na Wikipédia.", "link": "", "source": "wikipedia"})
            return jsonify({
                "summary": resumo,
                "link": link,
                "source": "wikipedia"
            })
              # ... (código existente para "resumo" na Wikipedia) ...
    elif source in ["web", "g1.globo.com", "lupa.uol.com.br", "firstdraftnews.org"]:
        dominio = source if source != "web" else None
        resumo_web, link_web = pesquisar_na_web_externa(termo, dominio)
        return jsonify({
            "summary": resumo_web,
            "link": link_web,
            "source": source
        })
    else:
        return jsonify({"error": "Fonte de pesquisa inválida."}), 400
        
if __name__ == '__main__':
    app.run(debug=True)