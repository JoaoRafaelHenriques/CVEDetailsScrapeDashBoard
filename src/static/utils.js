function isElementOverflowing(element) {
    // Verificamos se o texto ultrapassa o tamanho da DIV horizontalmente e verticalmente
    let isOverflowingHorizontally = element.scrollWidth > element.clientWidth;
    let isOverflowingVertically = element.scrollHeight > element.clientHeight;
    return isOverflowingHorizontally || isOverflowingVertically;
}

function popUp(element, value) {
    // Se o texto não passa a DIV não é preciso PopUp
    if (!isElementOverflowing(element)) {
        console.log('O texto não é maior que o elemento.');
    } else {
        // Vamos buscar a DIV do PopUp e preenchemos
        console.log('O texto');
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