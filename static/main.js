function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('collapsed');
}

// Executa o script apenas depois que a página HTML for totalmente carregada
document.addEventListener("DOMContentLoaded", function () {
    
    document.querySelectorAll(".nf-filha-input").forEach(input => {
        input.addEventListener("change", function () {
            let doc = this.dataset.doc;
            let row = this.dataset.id;
            let value = this.value;

            fetch("/salvar_nf_filha", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    doc: doc,
                    row: row,
                    value: value
                })
            });
        });
    });

    // Função para somar os valores das colunas e exibir os totais
    function somarValoresTabela() { 
        // Inicializa todas as variáveis de total ANTES do loop
        let totalLiquido = 0;
        let totalBruto = 0;
        let totalPis = 0;
        let totalCofins = 0;
        let totalIcms = 0;
        let totalSemFrete = 0; // Move a declaração para fora do loop

        // Seleciona todas as linhas no corpo da tabela (<tbody>)
        const linhas = document.querySelectorAll("#tabela tbody tr");

        linhas.forEach(linha => {
            const celulas = linha.querySelectorAll('td');

            // Extrai a descrição da coluna 1 (índice 0)
            const descricao = celulas[0].textContent.trim();

            // Extrai os valores das células e converte de string para número
            // As posições [9], [11], etc. referem-se ao índice da coluna.
            const valorLiquido = parseFloat(celulas[9].textContent.replace(',', '.'));
            const valorBruto = parseFloat(celulas[11].textContent.replace(',', '.'));
            const valorPis = parseFloat(celulas[13].textContent.replace(',', '.'));
            const valorCofins = parseFloat(celulas[14].textContent.replace(',', '.'));
            const valorIcms = parseFloat(celulas[15].textContent.replace(',', '.'));
            
            // Lógica para somar o valor da coluna 2, excluindo "FRETE INTERNACIONAL"
            if (descricao !== "FRETE INTERNACIONAL") {
                const valorSemFreteAtual = parseFloat(celulas[1].textContent.replace(',', '.'));
                
                if (!isNaN(valorSemFreteAtual)) {
                    totalSemFrete += valorSemFreteAtual;
                }
            }

            // Verifica se o valor é um número válido antes de somar
            if (!isNaN(valorLiquido)) totalLiquido += valorLiquido;
            if (!isNaN(valorBruto)) totalBruto += valorBruto;
            if (!isNaN(valorPis)) totalPis += valorPis;
            if (!isNaN(valorCofins)) totalCofins += valorCofins;
            if (!isNaN(valorIcms)) totalIcms += valorIcms;
        });

        // Exibe os totais nas células do rodapé (<tfoot>)
        // Certifique-se de que os IDs existam no seu arquivo index.html
        document.getElementById('totalLiquido').textContent = totalLiquido.toFixed(2).replace('.', ',');
        document.getElementById('totalBruto').textContent = totalBruto.toFixed(2).replace('.', ',');
        document.getElementById('totalPis').textContent = totalPis.toFixed(2).replace('.', ',');
        document.getElementById('totalCofins').textContent = totalCofins.toFixed(2).replace('.', ',');
        document.getElementById('totalIcms').textContent = totalIcms.toFixed(2).replace('.', ',');
        document.getElementById('totalSemFrete').textContent = totalSemFrete.toFixed(2).replace('.', ',');
        
        

        // Logs para conferência
        console.log("Total Líquido: ", totalLiquido.toFixed(2));
        console.log("Total Bruto: ", totalBruto.toFixed(2));
        console.log("Total PIS: ", totalPis.toFixed(2));
        console.log("Total COFINS: ", totalCofins.toFixed(2));
        console.log("Total ICMS: ", totalIcms.toFixed(2));
        console.log("Total sem Frete: ", totalSemFrete.toFixed(2));
    }

    somarValoresTabela();

});