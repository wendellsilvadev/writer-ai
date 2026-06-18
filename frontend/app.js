// ============== CONFIGURAÇÃO ============== //
const API_BASE_URL = '/api';
const MIN_CHARS = 10;
const STORAGE_KEY = 'writerAI_history';

// ============== DOM ELEMENTS ============== //
const textInput = document.getElementById('textInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const charCount = document.getElementById('charCount');
const resultsPanel = document.getElementById('resultsPanel');
const loadingState = document.getElementById('loadingState');
const resultsContent = document.getElementById('resultsContent');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');
const historyList = document.getElementById('historyList');

let sentimentChart = null;

// ============== EVENT LISTENERS ============== //
textInput.addEventListener('input', handleTextInput);
analyzeBtn.addEventListener('click', handleAnalyze);
clearHistoryBtn.addEventListener('click', handleClearHistory);

// ============== HANDLERS ============== //
function handleTextInput() {
    const text = textInput.value;
    const length = text.length;
    
    // Update character count
    charCount.textContent = `${length} caracteres`;
    
    // Enable/disable button
    analyzeBtn.disabled = length < MIN_CHARS;
}

async function handleAnalyze() {
    const text = textInput.value.trim();
    
    if (text.length < MIN_CHARS) {
        showError('Texto deve ter pelo menos 10 caracteres');
        return;
    }
    
    analyzeBtn.disabled = true;
    resultsPanel.style.display = 'block';
    loadingState.style.display = 'flex';
    resultsContent.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ texto: text })
        });
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        displayResults(data);
        saveToHistory(text, data);
        showSuccess('Análise concluída com sucesso!');
        
    } catch (error) {
        console.error('Erro:', error);
        showError(`Erro ao analisar: ${error.message}`);
    } finally {
        analyzeBtn.disabled = false;
        loadingState.style.display = 'none';
    }
}

// ============== DISPLAY RESULTS ============== //
function displayResults(data) {
    // Exibir tone
    displayTone(data);
    
    // Exibir sentimentos
    displaySentiments(data);
    
    // Exibir insight
    displayInsight(data);
    
    // Exibir engajamento
    displayEngagement(data);
    
    // Exibir dados brutos
    displayRawData(data);
    
    resultsContent.style.display = 'block';
}

function displayTone(data) {
    const toneBadge = document.getElementById('toneBadge');
    const toneDescription = document.getElementById('toneDescription');
    
    toneBadge.textContent = capitalizeFirstLetter(data.tom_predominante);
    toneBadge.style.background = getToneColor(data.tom_predominante);
    
    // Confiança do sentimento
    const sentimentos = data.sentimentos;
    const maxConfidence = Math.max(...Object.values(sentimentos));
    const confidence = Math.round(maxConfidence * 100);
    
    toneDescription.textContent = `Confiança: ${confidence}%`;
}

function displaySentiments(data) {
    const sentimentsGrid = document.getElementById('sentimentsGrid');
    sentimentsGrid.innerHTML = '';
    
    const sentimentos = data.sentimentos;
    const sentimentNames = Object.keys(sentimentos).sort();
    
    // Criar gráfico de pizza
    createSentimentChart(sentimentos);
    
    // Criar cards de sentimentos
    sentimentNames.forEach(name => {
        const value = sentimentos[name];
        const percentage = (value * 100).toFixed(1);
        
        const card = document.createElement('div');
        card.className = 'sentiment-item';
        card.innerHTML = `
            <div class="sentiment-name">${capitalizeFirstLetter(name)}</div>
            <div class="sentiment-bar">
                <div class="sentiment-bar-fill" style="width: ${percentage}%"></div>
            </div>
            <div class="sentiment-value">${percentage}%</div>
        `;
        
        sentimentsGrid.appendChild(card);
    });
}

function createSentimentChart(sentimentos) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    
    // Destruir gráfico anterior se existir
    if (sentimentChart) {
        sentimentChart.destroy();
    }
    
    const labels = Object.keys(sentimentos).map(name => capitalizeFirstLetter(name));
    const values = Object.values(sentimentos);
    const colors = [
        '#6366f1', // positivo
        '#ef4444', // negativo
        '#94a3b8', // neutro
        '#a78bfa', // angustiante
        '#f97316', // misto
        '#10b981', // esperancoso
        '#3b82f6', // filosofico
        '#8b5cf6'  // melancolico
    ];
    
    sentimentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: 'white',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { size: 12 },
                        padding: 15
                    }
                }
            }
        }
    });
}

function displayInsight(data) {
    const insightText = document.getElementById('insightText');
    insightText.textContent = data.insight;
}

function displayEngagement(data) {
    const engagementBadge = document.getElementById('engagementBadge');
    const engagementConfidence = document.getElementById('engagementConfidence');
    
    const engagementClass = data.engajamento.toLowerCase();
    const confidence = Math.round(data.confianca_engajamento * 100);
    
    engagementBadge.textContent = data.engajamento;
    engagementBadge.className = `engagement-badge ${engagementClass}`;
    
    engagementConfidence.innerHTML = `
        <h4>Confiança da Predição</h4>
        <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${confidence}%"></div>
        </div>
        <div class="confidence-percent">${confidence}%</div>
    `;
}

function displayRawData(data) {
    const rawDataCode = document.getElementById('rawDataCode');
    rawDataCode.textContent = JSON.stringify(data, null, 2);
}

// ============== HISTORY ============== //
function saveToHistory(text, result) {
    let history = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    
    history.unshift({
        id: Date.now(),
        text: text,
        tone: result.tom_predominante,
        engagement: result.engajamento,
        timestamp: new Date().toLocaleString('pt-BR')
    });
    
    // Manter últimas 20 análises
    history = history.slice(0, 20);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    
    loadHistory();
}

function loadHistory() {
    const history = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    historyList.innerHTML = '';
    
    if (history.length === 0) {
        historyList.innerHTML = '<p style="color: var(--text-light); font-size: 0.9em;">Nenhuma análise realizada ainda</p>';
        return;
    }
    
    history.forEach(item => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <div class="history-item-text">${item.text.substring(0, 50)}...</div>
            <div class="history-item-meta">
                ${item.tone} • ${item.engagement} • ${item.timestamp}
            </div>
        `;
        
        historyItem.addEventListener('click', () => {
            textInput.value = item.text;
            textInput.dispatchEvent(new Event('input'));
            textInput.focus();
        });
        
        historyList.appendChild(historyItem);
    });
}

function handleClearHistory() {
    if (confirm('Tem certeza que deseja limpar o histórico?')) {
        localStorage.removeItem(STORAGE_KEY);
        loadHistory();
        showSuccess('Histórico limpo');
    }
}

// ============== UTILITIES ============== //
function capitalizeFirstLetter(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function getToneColor(tone) {
    const colors = {
        'positivo': 'linear-gradient(135deg, #10b981, #059669)',
        'negativo': 'linear-gradient(135deg, #ef4444, #dc2626)',
        'neutro': 'linear-gradient(135deg, #94a3b8, #64748b)',
        'angustiante': 'linear-gradient(135deg, #a78bfa, #7c3aed)',
        'misto': 'linear-gradient(135deg, #f97316, #ea580c)',
        'esperancoso': 'linear-gradient(135deg, #06b6d4, #0891b2)',
        'filosofico': 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
        'melancolico': 'linear-gradient(135deg, #8b5cf6, #7c3aed)'
    };
    
    return colors[tone.toLowerCase()] || 'linear-gradient(135deg, #6366f1, #8b5cf6)';
}

function showError(message) {
    const toast = document.getElementById('errorToast');
    toast.textContent = message;
    toast.style.display = 'block';
    
    setTimeout(() => {
        toast.style.display = 'none';
    }, 5000);
}

function showSuccess(message) {
    const toast = document.getElementById('successToast');
    toast.textContent = message;
    toast.style.display = 'block';
    
    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

// ============== INITIALIZATION ============== //
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ Writer AI Frontend Loaded');
    loadHistory();
    handleTextInput();
});
