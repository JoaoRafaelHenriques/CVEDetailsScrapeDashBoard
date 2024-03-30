window.onload = function() {
    
    let queryString = window.location.search;
    let urlParams = new URLSearchParams(queryString);
    queryString = urlParams.get("Projeto");

    // Pedimos os dados ao flask
    fetch('/grafico/?Projeto=' + queryString)
    .then(response => {

        // Verificando se a solicitação foi bem-sucedida (status 200)
        if (!response.ok) {
            throw new Error('Erro ao buscar os dados.');
        }
        // Convertendo a resposta para JSON
        return response.json();
    })
    .then(data => {

        // {"Data": {Ano: num}, "Titulos": [[],[],[]]}
        console.log(data);

        // Mexemos nos dados agora
        let X1 = Object.keys(data.Data[0]);
        let Y1 = Object.values(data.Data[0]);
        let Y2 = Object.values(data.Data[1]);
        let Y3 = Object.values(data.Data[2]);
        let Y4 = Object.values(data.Data[3]);
        let Y5 = Object.values(data.Data[4]);

        let ctx = document.getElementById('myChart');

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
        // Lidando com erros
        console.log(error);
    });
};