document.getElementById('searchButton').addEventListener('click', performSearch);
document.getElementById('searchInput').addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        performSearch();
    }
});
document.getElementById('toggleSource').addEventListener('click', () => {
    const currentSource = document.getElementById('currentSource');
    const toggleButton = document.getElementById('toggleSource');

    if (currentSource.textContent.includes('Wikipedia')) {
        currentSource.textContent = 'Fonte: Web';
        toggleButton.textContent = 'Trocar para Wikipedia';
    } else {
        currentSource.textContent = 'Fonte: Wikipedia';
        toggleButton.textContent = 'Trocar para Web';
    }
});

async function performSearch() {
    const query = document.getElementById('searchInput').value;
    const type = document.querySelector('input[name="type"]:checked').value;
    const currentSource = document.getElementById('currentSource').textContent;
    const isWikipedia = currentSource.includes('Wikipedia');
    const resultsDiv = document.getElementById('results');

    if (!query) {
        resultsDiv.textContent = 'Por favor, digite um termo para pesquisar.';
        return;
    }

    resultsDiv.textContent = 'Carregando...';

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                source: isWikipedia ? 'wikipedia' : 'web',
                type: type
            })
        });

        const data = await response.json();

        if (response.status !== 200) {
            resultsDiv.textContent = `Erro: ${data.error}`;
            return;
        }

        if (data.full_text) {
            // Nova lógica de formatação
            let formattedText = data.full_text;

            // Divide o texto em blocos de parágrafos/listas
            const blocks = formattedText.split('\n\n');
            let htmlContent = '';

            blocks.forEach(block => {
                if (block.startsWith('## ')) {
                    // Título
                    htmlContent += `<h2>${block.substring(3)}</h2>`;
                } else if (block.includes('•')) {
                    // Lista
                    htmlContent += '<ul>';
                    const listItems = block.split('\n').filter(item => item.trim() !== '');
                    listItems.forEach(item => {
                        htmlContent += `<li>${item.substring(2).trim()}</li>`;
                    });
                    htmlContent += '</ul>';
                } else {
                    // Parágrafo
                    htmlContent += `<p>${block}</p>`;
                }
            });

            resultsDiv.innerHTML = htmlContent;
        } else {
            resultsDiv.innerHTML = data.summary.replace(/\n/g, '<br>');
        }
        
        if (data.link) {
            resultsDiv.innerHTML += '<br><br>clique no link e leia mais sobre o assunto<br><br>';
            const link = document.createElement('a');
            link.href = data.link;
            link.textContent = data.link;
            link.target = '_blank';
            link.classList.add('result-link');
            resultsDiv.appendChild(link);
        }

    } catch (error) {
        resultsDiv.textContent = `Ocorreu um erro na comunicação: ${error}`;
    }
}
async function performSearch() {
    const query = document.getElementById('searchInput').value;
    const type = document.querySelector('input[name="type"]:checked').value;
    const currentSource = document.getElementById('currentSource').textContent;
    const isWikipedia = currentSource.includes('Wikipedia');
    const resultsDiv = document.getElementById('results');

    if (!query) {
        resultsDiv.textContent = 'Por favor, digite um termo para pesquisar.';
        return;
    }

    resultsDiv.textContent = 'Carregando...';

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                source: isWikipedia ? 'wikipedia' : 'web',
                type: type
            })
        });

        const data = await response.json();

        if (response.status !== 200) {
            resultsDiv.textContent = `Erro: ${data.error}`;
            return;
        }

        if (data.full_text) {
            // Processa o texto para a opção "Tudo"
            let formattedText = data.full_text
                .replace(/^## (.*)$/gm, '<h2>$1</h2>')  // Títulos h2
                .replace(/^  • (.*)$/gm, '<li>$1</li>') // Listas
                .replace(/\n\n/g, '<p></p>');             // Parágrafos

            resultsDiv.innerHTML = formattedText;
        } else {
            resultsDiv.innerHTML = data.summary.replace(/\n/g, '<br>');
        }
        
        if (data.link) {
            resultsDiv.innerHTML += '<br><br>clique no link e leia mais sobre o assunto<br><br>';
            const link = document.createElement('a');
            link.href = data.link;
            link.textContent = data.link;
            link.target = '_blank';
            link.classList.add('result-link');
            resultsDiv.appendChild(link);
        }

    } catch (error) {
        resultsDiv.textContent = `Ocorreu um erro na comunicação: ${error}`;
    }
}

async function performSearch() {
    const query = document.getElementById('searchInput').value;
    const type = document.querySelector('input[name="type"]:checked').value;
    const source = document.getElementById('searchSource').value; // Pega o valor do select
    const resultsDiv = document.getElementById('results');

    if (!query) {
        resultsDiv.textContent = 'Por favor, digite um termo para pesquisar.';
        return;
    }

    resultsDiv.textContent = 'Carregando...';

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                source: source, // Envia a fonte selecionada
                type: type
            })
        });

        const data = await response.json();


        if (response.status !== 200) {
            resultsDiv.textContent = `Erro: ${data.error}`;
            return;
        }

        if (data.full_text) {
            resultsDiv.innerHTML = data.full_text;
        } else {
            resultsDiv.innerHTML = data.summary.replace(/\n/g, '<br>');
        }
        
        if (data.link) {
            resultsDiv.innerHTML += '<br><br>clique no link e leia mais sobre o assunto<br><br>';
            const link = document.createElement('a');
            link.href = data.link;
            link.textContent = data.link;
            link.target = '_blank';
            link.classList.add('result-link');
            resultsDiv.appendChild(link);
        }

    } catch (error) {
        resultsDiv.textContent = `Ocorreu um erro na comunicação: ${error}`;
    }
}