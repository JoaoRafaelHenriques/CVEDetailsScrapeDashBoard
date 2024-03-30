// Acontece sempre que a página carrega
window.onload = function() {

    // Obtemos o valor do parâmetro "Page" da URL
    let [url, search_params, page] = url_tratamento();
    
    // Atualizamos o texto do link com o valor do parâmetro "Page"
    document.getElementById("numero").textContent = page;
};

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

function esquerda(){
    // Atualizamos o valor da pagina no url
    let [url, search_params, page] = url_tratamento();
    if (page > 1){
        search_params.set("Page", page - 1)
    }
    url_atualiza(url, search_params);
}

function direita(){
    // Atualizamos o valor da pagina no url
    let [url, search_params, page] = url_tratamento();
    search_params.set("Page", page + 1)
    url_atualiza(url, search_params);
}