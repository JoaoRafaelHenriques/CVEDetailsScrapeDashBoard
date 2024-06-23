let graficoChart = null;
const colors = ["#B07156", "#413C58", "#EDF060", "#33673B", "#00A6FB"]

// Acontece sempre que a página carrega
window.addEventListener("load",function() {
    grafico()
},false);

// Atualizamos o gráfico quando há uma pesquisa filtrada
function atualizaGrafico(event){
    event.preventDefault();
    let valores = document.querySelector(".barraTexto").value;
    let cwes = valores.trim().split(" ");
    // Removemos duplicados e espaços em branco ou vazios
    cwes = cwes.filter((cwe, index) => cwe !== "" && cwe !== " " && cwes.indexOf(cwe) === index && /^\d+$/.test(cwe));
    if (cwes.length > 5) cwes = cwes.slice(0,5);
    grafico(cwes); 
} 

function getUrlParam(){
    // Obtemos o URL
    let queryString = window.location.search;
    // Procuramos pelos parâmetros e retornamos o Projeto
    let urlParams = new URLSearchParams(queryString);
    return urlParams.get("Projeto");
}

function grafico(cwes){

    if (graficoChart) {
        graficoChart.destroy();
    }
    
    // Obtemos o projeto
    queryString = getUrlParam();
    
    // Construimos o URL
    let url = '/grafico/?Projeto=' + queryString;

    // Vemos se há filtros
    if (cwes) {
        url = url + '&CWES=' + cwes;
    }
    
    // Pedimos os dados ao flask com o parâmetro
    fetch(url)
    .then(response => {

        // Verificamos se tudo está correto
        if (!response.ok) {
            throw new Error('Erro ao buscar os dados.');
        }
        // Convertemos a resposta para JSON
        return response.json();
    })
    .then(data => {

        console.log(data);
        if (data.Data.length === 0){
            return;
        }

        // {"Data": {Ano: num, Ano: num, Ano: num, etc}, "Titulos": [[],[],[]]}
        let anos = Object.keys(data.Data[0]);

        
        // Onde queremos colocar o gráfico no HTML
        let ctx = document.getElementById('myChart');

        let datasets = data.Titulos.map((titulo, index) => ({
            label: titulo,
            data: Object.values(data.Data[index]),
            borderWidth: 1,
            backgroundColor: colors[index],
            borderColor: colors[index]
        }));

        // Contruímos o gráfico
        graficoChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: anos,
                datasets: datasets
            },
            options: {
                layout: {
                    padding: 20
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    })
    .catch(error => {
        // Lidamos com possíveis erros
        console.log(error);
    });
} 

function download() {
    const originalCanvas = document.getElementById('myChart');
    const width = originalCanvas.width;
    const height = originalCanvas.height;

    // Criar um canvas temporário com as mesmas dimensões
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = width;
    tempCanvas.height = height;
    const tempCtx = tempCanvas.getContext('2d');

    // Desenhar o fundo branco
    tempCtx.fillStyle = 'white';
    tempCtx.fillRect(0, 0, width, height);

    // Desenhar o conteúdo do gráfico original no canvas temporário
    tempCtx.drawImage(originalCanvas, 0, 0);

    // Criar o link para download
    const imageLink = document.createElement('a');
    imageLink.download = 'chart.png';
    imageLink.href = tempCanvas.toDataURL('image/png', 1.0);
    imageLink.click();
}