import requests
import urllib.parse
import tkinter as tk
from tkinter import scrolledtext, messagebox, END
import webbrowser
import threading
from bs4 import BeautifulSoup
from BuscadorWeb import pesquisar_na_web_externa

# Lista para armazenar o histórico de pesquisa
historico_pesquisa = []
MAX_HISTORICO = 10
MIN_HISTORICO_ALTURA = 5

def get_full_text_formatted(termo, text_widget):
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
        
        for tag in soup.find_all(['sup', 'table', 'aside', 'span', 'figure']):
            tag.extract()
            
        for element in soup.find('body').find_all(['p', 'h2', 'h3', 'h4', 'ul', 'ol', 'li']):
            if element.name == 'p':
                text = element.get_text(strip=True)
                if text:
                    text_widget.insert(END, text + '\n\n')
            elif element.name in ['h2', 'h3', 'h4']:
                text = element.get_text(strip=True)
                if text:
                    tag_name = element.name
                    text_widget.insert(END, text + '\n', tag_name)
                    text_widget.insert(END, '-' * 50 + '\n\n')
            elif element.name in ['ul', 'ol']:
                for item in element.find_all('li'):
                    text = item.get_text(strip=True)
                    if text:
                        text_widget.insert(END, '  • ' + text + '\n')
                text_widget.insert(END, '\n')

        return True
        
    except requests.exceptions.RequestException as e:
        text_widget.insert(END, f"Erro ao obter texto completo: {e}\n")
        return False
    except Exception as e:
        text_widget.insert(END, f"Ocorreu um erro inesperado ao processar o texto: {e}\n")
        return False

def pesquisar_wikipedia(termo, limite=3, tipo="resumo"):
    if tipo == "tudo":
        return True, ""

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

def atualizar_historico(termo):
    if termo in historico_pesquisa:
        historico_pesquisa.remove(termo)
    historico_pesquisa.insert(0, termo)
    if len(historico_pesquisa) > MAX_HISTORICO:
        historico_pesquisa.pop()
    listbox_historico.delete(0, END)
    for item in historico_pesquisa:
        listbox_historico.insert(END, item)
    listbox_historico.config(height=max(len(historico_pesquisa), MIN_HISTORICO_ALTURA))

def usar_historico(event):
    selecionado = listbox_historico.curselection()
    if selecionado:
        termo = listbox_historico.get(selecionado[0])
        entrada.delete(0, END)
        entrada.insert(0, termo)
        buscar()

def sugerir_titulos_wikipedia(termo):
    url = f"https://pt.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(termo)}&limit=10&format=json"
    try:
        response = requests.get(url, timeout=1)
        response.raise_for_status()
        dados = response.json()
        return dados[1]
    except (requests.exceptions.RequestException, IndexError):
        return []

def autocomplete(event):
    termo = entrada.get()
    if len(termo) < 2:
        listbox_sugestoes.pack_forget()
        return
    thread = threading.Thread(target=atualizar_sugestoes, args=(termo,))
    thread.start()

def atualizar_sugestoes(termo):
    sugestoes = sugerir_titulos_wikipedia(termo)
    if sugestoes:
        listbox_sugestoes.delete(0, END)
        for sugestao in sugestoes:
            listbox_sugestoes.insert(END, sugestao)
        listbox_sugestoes.pack(fill="x", pady=(0,5))
    else:
        listbox_sugestoes.pack_forget()

def usar_sugestao(event):
    selecionado = listbox_sugestoes.curselection()
    if selecionado:
        termo = listbox_sugestoes.get(selecionado[0])
        entrada.delete(0, END)
        entrada.insert(0, termo)
        listbox_sugestoes.pack_forget()

def buscar():
    termo = entrada.get().strip()
    if not termo:
        messagebox.showwarning("Atenção", "Por favor, digite um termo para pesquisar.")
        return
    listbox_sugestoes.pack_forget()
    tipo = opcao.get()
    try:
        limite_str = entrada_limite.get().strip()
        limite = int(limite_str) if tipo in ["palavras"] else None
        if tipo in ["palavras"] and not limite_str.isdigit():
            messagebox.showwarning("Atenção", "O limite deve ser um número inteiro.")
            return
        if limite is not None and limite <= 0:
            messagebox.showwarning("Atenção", "O limite deve ser um número positivo.")
            return
    except ValueError:
        messagebox.showwarning("Atenção", "O limite deve ser um número inteiro.")
        return

    texto_resultado.delete(1.0, END)
    
    if tipo == "tudo":
        texto_resultado.insert(END, f"Carregando texto completo de '{termo}'...\n")
        thread_busca = threading.Thread(target=lambda: get_full_text_formatted(termo, texto_resultado))
        thread_busca.start()
        link = f"https://pt.wikipedia.org/wiki/{urllib.parse.quote(termo)}"
        link_label = tk.Label(texto_resultado, text=f"Leia mais em: {link}", fg="blue", cursor="hand2")
        texto_resultado.window_create(END, window=link_label)
        atualizar_historico(termo)
    else:
        resumo, link = pesquisar_wikipedia(termo, limite, tipo)

        if link == "404":
            texto_resultado.insert(END, "Página não encontrada na Wikipédia. Buscando na internet...\n\n")
            resumo_web, link_web = pesquisar_na_web_externa(termo)
            texto_resultado.insert(END, resumo_web)
            if link_web:
                # Novo: Adiciona a frase antes do link da web
                texto_resultado.insert(END, "clique no link e leia mais sobre o assunto\n\n")
                link_label = tk.Label(texto_resultado, text=f"Acessar: {link_web}", fg="blue", cursor="hand2")
                link_label.bind("<Button-1>", lambda e: webbrowser.open(link_web))
                texto_resultado.window_create(END, window=link_label)
        else:
            texto_resultado.insert(END, resumo)
            if link:
                # Novo: Adiciona a frase antes do link da Wikipedia
                texto_resultado.insert(END, f"\n\nclique no link e leia mais sobre o assunto\n\n")
                link_label = tk.Label(texto_resultado, text=link, fg="blue", cursor="hand2")
                link_label.bind("<Button-1>", lambda e: webbrowser.open(link))
                texto_resultado.window_create(END, window=link_label)
            atualizar_historico(termo)

# Criar janela principal
janela = tk.Tk()
janela.title("Pesquisa na Wikipédia")
janela.geometry("850x500")
janela.configure(padx=10, pady=10)

texto_resultado = scrolledtext.ScrolledText(janela, wrap=tk.WORD, width=70, height=15, font=("Arial", 10))
texto_resultado.tag_configure('h2', font=('Arial', 14, 'bold'))
texto_resultado.tag_configure('h3', font=('Arial', 12, 'bold'))
texto_resultado.tag_configure('h4', font=('Arial', 11, 'bold'))
texto_resultado.tag_configure('bold', font=('Arial', 10, 'bold'))
texto_resultado.tag_configure('italic', font=('Arial', 10, 'italic'))

main_frame = tk.Frame(janela)
main_frame.pack(fill=tk.BOTH, expand=True)

painel_esquerdo = tk.Frame(main_frame)
painel_esquerdo.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

tk.Label(painel_esquerdo, text="Histórico de Pesquisa").pack(pady=(0, 5))
listbox_historico = tk.Listbox(painel_esquerdo, width=30)
listbox_historico.pack(fill=tk.Y)
listbox_historico.bind("<<ListboxSelect>>", usar_historico)

painel_direito = tk.Frame(main_frame)
painel_direito.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

frame_busca = tk.Frame(painel_direito)
frame_busca.pack(pady=10)

tk.Label(frame_busca, text="Pesquisar:").grid(row=0, column=0, sticky="w", padx=5)

frame_entrada_sugestoes = tk.Frame(frame_busca)
frame_entrada_sugestoes.grid(row=0, column=1, padx=5)

entrada = tk.Entry(frame_entrada_sugestoes, width=50)
entrada.pack()
entrada.bind("<KeyRelease>", autocomplete)

listbox_sugestoes = tk.Listbox(frame_entrada_sugestoes, width=50, height=5)
listbox_sugestoes.bind("<<ListboxSelect>>", usar_sugestao)

tk.Button(frame_busca, text="Pesquisar", command=buscar).grid(row=0, column=2, padx=5)

frame_opcoes = tk.Frame(painel_direito)
frame_opcoes.pack(pady=5)

tk.Label(frame_opcoes, text="Limitar por:").grid(row=0, column=0, padx=5)
opcao = tk.StringVar(value="resumo")
tk.Radiobutton(frame_opcoes, text="Resumo", variable=opcao, value="resumo").grid(row=0, column=1)
tk.Radiobutton(frame_opcoes, text="Palavras", variable=opcao, value="palavras").grid(row=0, column=2)
tk.Radiobutton(frame_opcoes, text="Tudo", variable=opcao, value="tudo").grid(row=0, column=3)

tk.Label(frame_opcoes, text="Quantidade:").grid(row=0, column=4, padx=5)
entrada_limite = tk.Entry(frame_opcoes, width=5)
entrada_limite.grid(row=0, column=5)
entrada_limite.insert(0, "3")

texto_resultado.pack(pady=10, fill=tk.BOTH, expand=True)

janela.bind("<Return>", lambda event: buscar())

janela.mainloop()