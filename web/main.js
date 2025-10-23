// Logica JavaScript para a interface web do CNPJ X-Ray

// ** Funções expostas para Python chamar
// Função chamada pelo Python (eel.update_results_js) para adicionar um resultado ao log.
eel.expose(update_results_js);

// Função que atualiza o log de resultados na interface web
function update_results_js(result_json_string) {

    const resultsLog = document.getElementById('results-log');
    const result = JSON.parse(result_json_string);

    // Cria um novo elemento <pre> para o bloco de resultado
    const resultBlock = document.createElement('pre');
    resultBlock.classList.add('result-block');

    let output = '';

    if (result.status === 'success') {

        resultBlock.classList.add('result-success');
        output = `<b>SUCESSO:</b> ${result.cnpj} - ${result.razao_social}\n\n` + 
                 `Classificação: ${result.data.classificacao} (Score: ${result.data.score})\n` +
                 `Justificativas: \n\t${result.data.justificativas.length > 0 ? result.data.justificativas.join(', ') : '-'}`;
    
    } else {

        resultBlock.classList.add('result-error');
        output = `<b>ERRO:</b> ${result.cnpj}\n\n` + `Mensagem: ${result.message}`;

    }
    
    resultBlock.textContent = output;
    resultsLog.appendChild(resultBlock);
    
    // Auto-scroll para o novo resultado
    resultsLog.scrollTop = resultsLog.scrollHeight;
}

// Função chamada pelo Python (eel.processing_complete_js) quando todo termina.
eel.expose(processing_complete_js);

function processing_complete_js() {

    const button = document.getElementById('analyze-button');
    button.disabled = false;
    button.textContent = 'Analisar CNPJs';
    
    const resultsLog = document.getElementById('results-log');
    resultsLog.innerHTML += "\n<small>** Processamento Concluído **</small>";
    resultsLog.scrollTop = resultsLog.scrollHeight;

}


// --- Função chamada pelo HTML ---

// Função click do botão "Analisar CNPJs"
function start_analysis() {

    const button = document.getElementById('analyze-button');
    const textarea = document.getElementById('cnpj-input');
    const resultsLog = document.getElementById('results-log');
    
    const cnpjs_text = textarea.value;
    const cnpj_list = cnpjs_text.split('\n').filter(Boolean); // Divide por linha e remove vazias

    if (cnpj_list.length === 0) {
        alert('Por favor, insira pelo menos um CNPJ.');
        return;
    }

    // Desabilita o botão e limpa o log
    button.disabled = true;
    button.textContent = 'Analisando...';
    resultsLog.innerHTML = '<small>** Iniciando análise... **</small>'; // Limpa o log

    // Chama a função Python 'analyze_cnpj' e passa a lista de CNPJs.
    eel.analyze_cnpj(cnpj_list);

}