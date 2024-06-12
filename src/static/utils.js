function isElementOverflowing(element) {
    // Verificamos se o texto ultrapassa o tamanho da DIV horizontalmente e verticalmente
    let isOverflowingHorizontally = element.scrollWidth > element.clientWidth;
    let isOverflowingVertically = element.scrollHeight > element.clientHeight;
    return isOverflowingHorizontally || isOverflowingVertically;
}

function popUp(element) {
    let value = element.innerText;

    // Se o texto não passa a DIV não é preciso PopUp
    if (!element || !value){
        return;
    } 

    if (!isElementOverflowing(element)) {
        console.log('O texto não é maior que o elemento.');
    } else {
        // Vamos buscar a DIV do PopUp e preenchemos
        let popUpDiv = document.getElementById('popUp');
        popUpDiv.innerHTML = value;
        popUpDiv.style.display = 'inline';

        // Calculamos as coordenadas para o PopUp
        let colunaTD = element.getBoundingClientRect();
        let popUpRect = popUpDiv.getBoundingClientRect();

        // A posição será logo a seguir à coluna mas encima da mesma
        popUpDiv.style.left = (colunaTD.right) + 'px';
        popUpDiv.style.top = (colunaTD.top - popUpRect.height) + 'px';
    }
}

function hidePopUp() {
    // Escondemos o PopUp
    let popUpDiv = document.getElementById('popUp');
    popUpDiv.style.display = 'none';
}


function popUpResume(element) {    
    // Vamos buscar a DIV do PopUp e preenchemos
    let popUpDiv = document.getElementById('popUpInfo');
    popUpDiv.style.display = 'inline';

    // Calculamos as coordenadas para o PopUp
    let colunaTD = element.getBoundingClientRect();
    let popUpRect = popUpDiv.getBoundingClientRect();

    // A posição será logo a seguir à coluna mas encima da mesma
    popUpDiv.style.left = (colunaTD.right) + 'px';
    popUpDiv.style.top = (colunaTD.top - popUpRect.height) + 'px';
}

function informationPatchPID(element){
    // Recebemos um elemento com um pathe
    const commit = element.innerText;

    // Vamos buscar o ID do patche na base de dados
    const url_pid = '/find/p_id/?P_ID=' + commit;
    const p_ids = fetch(url_pid)
    .then(response => {
        
        // Verificamos se tudo está correto
        if (!response.ok) {
            throw new Error('Erro ao buscar os dados.');
        }
        // Convertemos a resposta para JSON
        return response.json();
    })
    .then(data => {
        // Retornamos os resultados
        return data.data;
    })
    .catch(error => {
        // Lidamos com possíveis erros
        console.log(error);
    });
    return p_ids;
}

async function informationPatch(element, _, project){
    // Esperamos que a informação chegue e se não trouxer nada, não retorna nada
    const functions = await informationPatchPID(element);
    if (functions.length === 0) {
        return;
    }
    // Vamos para a página que apresenta os resultados
    const json_array = JSON.stringify(functions);
    window.location.href = "/overview_patches/patch?info=" + encodeURIComponent(json_array) + "&commit=" + element.innerText + "&projeto=" + project;
}