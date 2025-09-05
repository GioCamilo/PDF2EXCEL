/**
 * Função para alternar o estado da sidebar (expandida/colapsada)
 */
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('collapsed');
}

/**
 * Executa o script apenas depois que a página HTML for totalmente carregada
 */
document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM carregado - Iniciando scripts...");

    // ===========================================
    // SEÇÃO 1: CONFIGURAÇÃO INICIAL DAS NF FILHAS
    // ===========================================
    
    /**
     * Define status inicial COM/SEM emissão baseado nos valores dos inputs
     */
    function configurarStatusInicialNF() {
        const inputs = document.querySelectorAll(".nf-filha-input");
        
        inputs.forEach(input => {
            const row = input.closest("tr");
            const emissaoCell = row ? row.querySelector(".emissao-nfe") : null;

            if (emissaoCell) {
                if (input.value.trim() !== "") {
                    // Input preenchido = COM EMISSÃO
                    emissaoCell.textContent = "COM EMISSÃO";
                    emissaoCell.classList.add("text-success");
                    emissaoCell.classList.remove("text-danger");
                } else {
                    // Input vazio = SEM EMISSÃO
                    emissaoCell.textContent = "SEM EMISSÃO";
                    emissaoCell.classList.add("text-danger");
                    emissaoCell.classList.remove("text-success");
                }
            }
        });
    }

    // ===========================================
    // SEÇÃO 2: EVENTOS DE MUDANÇA NOS INPUTS
    // ===========================================
    
    /**
     * Adiciona eventos para salvar alterações no backend
     */
    function adicionarEventosNF() {
        const inputs = document.querySelectorAll(".nf-filha-input");
        
        inputs.forEach(input => {
            input.addEventListener("change", function () {
                // Obtém dados do input alterado
                const doc = this.dataset.doc;
                const row = this.dataset.id;
                const value = this.value;

                // Validação básica dos dados
                if (!doc || !row) {
                    console.error("Dados insuficientes para salvar:", { doc, row, value });
                    return;
                }

                // Envia dados para o backend
                fetch("/salvar_nf_filha", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ doc, row, value })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Erro HTTP: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Dados salvos com sucesso:", data);
                    
                    // Atualiza o status visual após salvar
                    atualizarStatusEmissao(this);
                })
                .catch(error => {
                    console.error("Erro ao salvar dados:", error);
                    alert("Erro ao salvar. Tente novamente.");
                });
            });
        });
    }

    /**
     * Atualiza o status visual de emissão baseado no valor do input
     * @param {HTMLElement} input - O input que foi alterado
     */
    function atualizarStatusEmissao(input) {
        const row = input.closest("tr");
        const emissaoCell = row ? row.querySelector(".emissao-nfe") : null;

        if (emissaoCell) {
            if (input.value.trim() !== "") {
                emissaoCell.textContent = "COM EMISSÃO";
                emissaoCell.classList.add("text-success");
                emissaoCell.classList.remove("text-danger");
            } else {
                emissaoCell.textContent = "SEM EMISSÃO";
                emissaoCell.classList.add("text-danger");
                emissaoCell.classList.remove("text-success");
            }
        }
    }

    // ===========================================
    // SEÇÃO 3: CÁLCULO DOS TOTAIS DA TABELA
    // ===========================================
    
    /**
     * Função para somar os valores das colunas e exibir os totais
     */
    function somarValoresTabela() {
        console.log("Iniciando cálculo dos totais...");
        
        // Inicializa todas as variáveis de total
        let totalLiquido = 0;
        let totalBruto = 0;
        let totalPis = 0;
        let totalCofins = 0;
        let totalIcms = 0;
        let totalSemFrete = 0;

        // Seleciona todas as linhas no corpo da tabela
        const linhas = document.querySelectorAll("#tabela tbody tr");
        
        if (linhas.length === 0) {
            console.warn("Nenhuma linha encontrada na tabela #tabela tbody tr");
            return;
        }

        // Processa cada linha da tabela
        linhas.forEach((linha, index) => {
            const celulas = linha.querySelectorAll('td');
            
            if (celulas.length < 16) {
                console.warn(`Linha ${index + 1}: número insuficiente de células (${celulas.length})`);
                return;
            }

            // Extrai a descrição da primeira coluna
            const descricao = celulas[0].textContent.trim();

            // Função auxiliar para converter string para número
            const parseValor = (texto) => {
                if (!texto) return 0;
                const valor = parseFloat(texto.replace(',', '.'));
                return isNaN(valor) ? 0 : valor;
            };

            // Extrai os valores das células específicas
            const valorLiquido = parseValor(celulas[9]?.textContent);
            const valorBruto = parseValor(celulas[11]?.textContent);
            const valorPis = parseValor(celulas[13]?.textContent);
            const valorCofins = parseValor(celulas[14]?.textContent);
            const valorIcms = parseValor(celulas[15]?.textContent);

            // Soma valores gerais
            totalLiquido += valorLiquido;
            totalBruto += valorBruto;
            totalPis += valorPis;
            totalCofins += valorCofins;
            totalIcms += valorIcms;

            // Soma valor da coluna 2, excluindo "FRETE INTERNACIONAL"
            if (descricao !== "FRETE INTERNACIONAL") {
                const valorSemFreteAtual = parseValor(celulas[1]?.textContent);
                totalSemFrete += valorSemFreteAtual;
            }

            console.log(`Linha ${index + 1} (${descricao}):`, {
                liquido: valorLiquido,
                bruto: valorBruto,
                semFrete: descricao !== "FRETE INTERNACIONAL" ? parseValor(celulas[1]?.textContent) : 0
            });
        });

        // ===========================================
        // SEÇÃO 4: ATUALIZAÇÃO DOS ELEMENTOS HTML
        // ===========================================
        
        // Função auxiliar para formatar valores em moeda brasileira
        const formatarMoeda = (valor) => {
            return valor.toLocaleString('pt-BR', { 
                style: 'currency', 
                currency: 'BRL' 
            });
        };

        // Atualiza elementos HTML com os totais calculados
        const elementoTotalSemFrete = document.getElementById('totalSemFrete');
        const elementoTotalLiquido = document.getElementById('totalLiquido');
        const elementoFormulaCheck = document.getElementById('formulaCheck');

        // Verifica se os elementos existem antes de atualizar
        if (elementoTotalSemFrete) {
            elementoTotalSemFrete.textContent = formatarMoeda(totalSemFrete);
        } else {
            console.warn("Elemento #totalSemFrete não encontrado");
        }

        if (elementoTotalLiquido) {
            elementoTotalLiquido.textContent = formatarMoeda(totalLiquido);
        } else {
            console.warn("Elemento #totalLiquido não encontrado");
        }

        // Calcula e exibe a diferença (fórmula check)
        const formulaCheck = totalLiquido - totalSemFrete;
        if (elementoFormulaCheck) {
            elementoFormulaCheck.textContent = formatarMoeda(formulaCheck);
        } else {
            console.warn("Elemento #formulaCheck não encontrado");
        }

        // Logs para conferência e debug
        console.log("=== TOTAIS CALCULADOS ===");
        console.log("Total Líquido:", formatarMoeda(totalLiquido));
        console.log("Total Bruto:", formatarMoeda(totalBruto));
        console.log("Total PIS:", formatarMoeda(totalPis));
        console.log("Total COFINS:", formatarMoeda(totalCofins));
        console.log("Total ICMS:", formatarMoeda(totalIcms));
        console.log("Total sem Frete:", formatarMoeda(totalSemFrete));
        console.log("Fórmula Check (Líquido - Sem Frete):", formatarMoeda(formulaCheck));
        console.log("========================");
    }

    // ===========================================
    // SEÇÃO 5: EXECUÇÃO DAS FUNÇÕES
    // ===========================================
    
    try {
        // Executa configurações iniciais
        configurarStatusInicialNF();
        adicionarEventosNF();
        
        // Executa cálculo dos totais
        somarValoresTabela();
        
        console.log("Script inicializado com sucesso!");
        
    } catch (error) {
        console.error("Erro durante a inicialização:", error);
    }
});