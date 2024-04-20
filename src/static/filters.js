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
        
        const lista_filtros = [];
        prepare_screen(dropdown);

        // Ao clicar no elemento adicionamoso as classes que permitem que as opções apareçam
        select.addEventListener('click', () => {
            select.classList.toggle('select-clicked');
            caret.classList.toggle('caret-rotate');
            menuFilter.classList.toggle('menuFilter-open');
        });
        
        // Para cada uma que clicamos adicionamos à busca ou removemos
        options.forEach(option => {
            if (option.classList.contains("active")){
                lista_filtros.push(option.innerText);
            }
            option.addEventListener('click', () => {
                select.classList.remove('selected-clicked');
                caret.classList.remove('caret-rotate');
                menuFilter.classList.remove('menuFilter-open');

                // Se já tiver ativo removemos, caso contrário adicionamos
                if (option.classList.contains('active')) {
                    option.classList.remove('active');
                    lista_filtros.splice(lista_filtros.indexOf(option.innerText), 1);
                } else {
                    option.classList.add('active');
                    lista_filtros.push(option.innerText);
                }
                console.log(lista_filtros);
                if (lista_filtros.length > 1){
                    selected.innerText = "Multiple";
                } else if (lista_filtros.length < 1) {
                    selected.innerText = "No filter, please select at least one..."
                } else {
                    selected.innerText = lista_filtros[0];
                }
            });
        });
        let help = dropdown.querySelectorAll('.active');
            console.log(help);
            if (help.length > 1){
                selected.innerText = "Multiple";
            } else if (help.length == 1) {
                selected.innerText = help[0].innerText;
            } else {
                selected.innerText = "No filter, please select at least one...";
            }
    });
};

function prepare_screen(param_filter){
    const options = param_filter.querySelectorAll('.menuFilter li');
    let name = param_filter.id;

    let values = get_param_from_url(name);

    options.forEach(option => {
        if (values.includes(option.innerText)){
            option.classList.add('active');
        } else {
            option.classList.remove('active');
        }
    });
}

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

    let selected = document.querySelectorAll('.dropdown');
    let [url, search_params, _] = url_tratamento();
    
    // Cada selected será um parâmetro diferente
    // Cada um tem vários dentro
    selected.forEach(select => {
        let lista_de_valores = "";
        let values = select.querySelectorAll(".active");
        values.forEach(value => {
            lista_de_valores = lista_de_valores + "&" + value.innerText;
        });
        search_params.set(select.id, lista_de_valores.slice(1));
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