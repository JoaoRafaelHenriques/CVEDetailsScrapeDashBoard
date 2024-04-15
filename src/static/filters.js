// Acontece sempre que a página carrega
window.onload = function() {
    
    // Procuramos os dropdowns
    const dropdowns = document.querySelectorAll(".dropdown");

    dropdowns.forEach(dropdown => {

        // Vamos buscar os elementos
        const select = dropdown.querySelector('.select');
        const caret = dropdown.querySelector('.caret');
        const menuFilter = dropdown.querySelector('.menuFilter');
        const options = dropdown.querySelectorAll('.menuFilter li');
        const selected = dropdown.querySelector('.selected');
        let help = get_param_from_url(selected.id);
        if (help === "All" && selected.id === "Missing"){
            selected.innerText = "Válido";
        }
        else {
            selected.innerText = help;
        }

        // Adicionamos um elemento para clique quando clicamos no retangulo e adicionamos as classes que permitem ver o menu
        select.addEventListener('click', () => {
            select.classList.toggle('select-clicked');
            caret.classList.toggle('caret-rotate');
            menuFilter.classList.toggle('menuFilter-open');
        });
        
        // Adicionamos um evento para clique quando clicamos nas opções, sendo que a opção escolhida passa para o menu
        options.forEach(option => {
            option.addEventListener('click', () => {
                selected.innerText = option.innerText;
                select.classList.remove('selected-clicked');
                caret.classList.remove('caret-rotate');
                menuFilter.classList.remove('menuFilter-open');
                options.forEach(option => {
                    option.classList.remove('active');
                });
                option.classList.add('active');
            });
        });
    });

};

function get_param_from_url(param){
    let url = new URL(window.location.href);
    let search_params = url.searchParams;
    let help = search_params.get(param);
    if (help && help != ""){
        return help;
    }
    return "All";
}

function pesquisaFiltrada(){

    let selected = document.querySelectorAll('.selected');
    let [url, search_params, page] = url_tratamento();
    
    selected.forEach(select => {
        search_params.set(select.id, select.innerText);
    });

    let cwe_number = document.querySelector('.barraTexto');
    if (cwe_number) {
        search_params.set("CWE", cwe_number.value);
    }

    url_atualiza(url, search_params);
}

function url_tratamento(){
    // Obtemos o url e o parametro da pagina e retornamos tudo
    let url = new URL(window.location.href);
    let search_params = url.searchParams;
    let page = Number.parseInt(search_params.get("Page"));
    if (isNaN(page)){
        page = 1;
    }
    return [url, search_params, page];
}

function url_atualiza(url, search_params){
    // Atualizamos o url
    url.search = search_params.toString();
    window.location.href = url.toString();
}