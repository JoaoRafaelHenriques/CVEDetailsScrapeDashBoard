function atualizaGrafico(event){
    event.preventDefault();
    let valores = document.querySelector(".barraTexto").value;
    let cwes = valores.trim().split(" ");
    // Removemos duplicados e espaços em branco ou vazios
    cwes = cwes.filter((cwe, index) => cwe !== "" && cwe !== " " && cwes.indexOf(cwe) === index);
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

// Acontece sempre que a página carrega
window.addEventListener("load",function() {
    grafico()
},false);

let graficoChart = null;

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

        // {"Data": {Ano: num, Ano: num, Ano: num, etc}, "Titulos": [[],[],[]]}
        let anos = Object.keys(data.Data[0]);
        
        // Onde queremos colocar o gráfico no HTML
        let ctx = document.getElementById('myChart');

        let datasets = data.Titulos.map((titulo, index) => ({
            label: titulo,
            data: Object.values(data.Data[index]),
            borderWidth: 1,
            backgroundColor: `rgba(${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, 1)`,
            borderColor: `rgba(${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, 0.5)`
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