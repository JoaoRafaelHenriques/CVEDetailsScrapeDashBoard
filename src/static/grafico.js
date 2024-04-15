function getUrlParam(){
    // Obtemos o URL
    let queryString = window.location.search;
    // Procuramos pelos parâmetros e retornamos o Projeto
    let urlParams = new URLSearchParams(queryString);
    return urlParams.get("Projeto");
}

// Acontece sempre que a página carrega
window.addEventListener("load",function() {

    // Obtemos o projeto
    queryString = getUrlParam();

    // Pedimos os dados ao flask com o parâmetro
    fetch('/grafico/?Projeto=' + queryString)
    .then(response => {

        // Verificamos se tudo está correto
        if (!response.ok) {
            throw new Error('Erro ao buscar os dados.');
        }
        // Convertemos a resposta para JSON
        return response.json();
    })
    .then(data => {

        // {"Data": {Ano: num}, "Titulos": [[],[],[]]}
        // Colocamos todos os Y sabendo que o X é igual para todos
        let X1 = Object.keys(data.Data[0]);
        let Y1 = Object.values(data.Data[0]);
        let Y2 = Object.values(data.Data[1]);
        let Y3 = Object.values(data.Data[2]);
        let Y4 = Object.values(data.Data[3]);
        let Y5 = Object.values(data.Data[4]);
        
        // Onde queremos colocar o gráfico no HTML
        let ctx = document.getElementById('myChart');

        // COntruímos o gráfico
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: X1,
                datasets: [{
                        label: data.Titulos[0],
                        data: Y1,
                        borderWidth: 1,
                        backgroundColor: 'rgba(255,0,0,1)',
                        borderColor: 'rgba(255,0,0,0.5)'
                    },
                    {
                        label: data.Titulos[1],
                        data: Y2,
                        borderWidth: 1,
                        backgroundColor: 'rgba(0,255,0,1)',
                        borderColor: 'rgba(0,255,0,0.5)'
                    },
                    {
                        label: data.Titulos[2],
                        data: Y3,
                        borderWidth: 1,
                        backgroundColor: 'rgba(0,255,255,1)',
                        borderColor: 'rgba(0,255,255,0.5)'
                    },
                    {
                        label: data.Titulos[3],
                        data: Y4,
                        borderWidth: 1,
                        backgroundColor: 'rgba(255,255,0,1)',
                        borderColor: 'rgba(255,255,0,0.5)'
                    },
                    {
                        label: data.Titulos[4],
                        data: Y5,
                        borderWidth: 1,
                        backgroundColor: 'rgba(255,0,255,1)',
                        borderColor: 'rgba(255,0,255,0.5)'
                    }]
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
},false);