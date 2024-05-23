from flask import Flask
from . import configs, base_de_dados
from datetime import date, timedelta
import os
import requests

INFO_SERVER: configs.Server = None
INFO_BASE_DE_DADOS = None

def trata_info_vulnerabidade(dic: dict) -> dict:
    """Retira todos os Nones do dicionário para uma melhor apresentação.

    Args:
        dic (dict): dicionário com a informação da vulnerabilidade

    Returns:
        dict: dicionário sem None
    """
    keys = dic.keys()
    for key in keys:
        for values in dic[key]:
            for index, value in enumerate(values):
                if value == 'None':
                    values[index] = "-"
    return dic

def trata_missing(valor: str) -> str:
    """Receba o valor da coluna MISSING da tabela VULNERABILTIIES.
       Em caso de ser NULL troca para Válido, para ser fácil de entender no dashboard.

    Args:
        valor (str): valor da tabela

    Returns:
        str: novo valor
    """
    if valor is None:
        return "Valid"
    return valor

def trata_categorias(categorias: str) -> str:
    """Recebe a categoria vinda da base de dados na forma >a<><b<.
       Transforma em a | b.

    Args:
        categorias (str): categorias

    Returns:
        str: categorias
    """
    return categorias.strip("<>").replace("<>", " | ")

def leitura_ficheiro(caminho: str) -> int:
    """Lê um ficheiro e diz quantas linhas tem.

    Args:
        caminho (str): caminho para o ficheiro

    Returns:
        int: número de linhas
    """
    if os.path.exists(caminho):
        with open(caminho, "r") as file:
            # Retiramos os headers que ocupam uma linha
            return len(file.readlines()) - 1
    return 0        

def calculo_diffs_diarios() -> dict:
    """Observa os valores de CVE para o último dia que foram coletadas.

    Returns:
        dict: dicionario com informação {Projeto: [atualizadas, desaparecidas, iguais, novas]}
        data: data do dia em que foi feito o cálculo
    """
    
    # Obtemos a data na forma YYYY-MM-DD
    data_hoje = date.today()
    
    info = dict()
    data_validada: bool = False
    
    # Iteramos por todos os projetos
    for projeto in INFO_SERVER.projetos:
        
        # Vamos buscar o id do projeto
        r_id: int = INFO_BASE_DE_DADOS.obter_id_projeto(projeto["Nome"])
        
        # Testamos se já existe informação de hoje
        while not data_validada:
            resultado: list = INFO_BASE_DE_DADOS.consulta(f"SELECT COUNT(*) FROM DAILY WHERE DATE = '{data_hoje}';")
            if resultado[0][0] < 13:
                data_hoje = data_hoje - timedelta(days = 1)
            else:
                data_validada = True    
                        
        # Quando temos data e o projeto existe com coisas na tabela inserimos os dados
        resultado: list = INFO_BASE_DE_DADOS.consulta(f"SELECT UPDATED, MISSING, EQUAL, NEW FROM DAILY WHERE R_ID = {r_id} AND DATE = '{data_hoje}';")
        
        if len(resultado) > 0:
            info[projeto["Nome"]] = [resultado[0][0], resultado[0][1], resultado[0][2], resultado[0][3]]
        else:
            resultado: list = INFO_BASE_DE_DADOS.consulta(f"SELECT UPDATED, MISSING, EQUAL, NEW FROM DAILY WHERE R_ID = {r_id} AND DATE = '{data_hoje - timedelta(days = 1)}';")
            info[projeto["Nome"]] = [resultado[0][0], resultado[0][1], resultado[0][2], resultado[0][3]]
    
    return info, data_hoje

def obter_id_projeto(projeto: str) -> int:
    """Obtém o id do projeto através do seu nome.

    Args:
        projeto (str): projeto

    Returns:
        int: id do projeto
    """
    return INFO_BASE_DE_DADOS.obter_id_projeto(projeto)

def obter_projeto_com_id(r_id: int) -> str:
    """ Recebe um id e retorna o nome do projeto.
    
    Args:
        r_id (int): id do projeto
    
    Returns:
        str: nome do projeto
    """
    return INFO_BASE_DE_DADOS.obter_projeto_com_id(r_id)

def consulta_base_de_dados(pesquisa: str) -> list:
    """Faz uma pesquisa na base de dados e retorna a lista de resultados.

    Args:
        pesquisa (str): consulta desejada

    Returns:
        list: lista de linhas e colunas pedidas
    """
    return INFO_BASE_DE_DADOS.consulta(pesquisa)

def find_functions(p_id: int) -> dict:
    """Procuramos as functions através de um p_id

    Returns:
        dic: data: lista de functions encontrados
    """
    dic: dict = {}
    
    resultados = consulta_base_de_dados(f'SELECT * FROM FUNCTIONS_DATA WHERE P_ID = "{p_id}";');
    dic["data"] = []

    for linha in resultados:
        dic["data"].append(linha)
    
    return dic

def find_num_linhas_alterado_ficheiro_repositorio(projeto_nome: str, commit: str, ficheiro: str):
    """Enviamos um projeto, um commit e um ficheiro e retornamos as alterações que aí ocorreram.
    

    Args:
        projeto_nome (str): nome do projeto
        commit (str): commit_hash
        ficheiro (str): caminho do ficheiro

    Returns:
        dic: adicionadas e removidas como chave
    """
    
    projeto_repositorio: str = ""
    projeto_owner: str = ""
    for projeto in INFO_SERVER.projetos:
        if projeto["Nome"] == projeto_nome:
            projeto_repositorio = projeto["Repositorio"]
            projeto_owner = projeto["Dono"]
            break
    
    if projeto_repositorio == "":
        return {}
    
    url = f"https://api.github.com/repos/{projeto_owner}/{projeto_repositorio}/commits/{commit}"
    
    # Vamos buscar a informação do commmit
    response = requests.get(url)
    response.raise_for_status()
    commit_data = response.json()
    
    # Procuramos o ficheiro em questão e retornamos os valores
    files_changed = {}
    for file in commit_data['files']:
        if file['filename'] != ficheiro:
            continue
        files_changed = {
            'adicionadas': file['additions'],
            'removidas': file['deletions']
        }
    
    return files_changed

def inicializa(app: Flask):
    """Inicializa as variáveis INFO_SERVER, INFO_BASE_DE_DADOS para serem usadas nas restantes
    funções.

    Args:
        app (Flask): aplicação Flask
    """
    global INFO_SERVER, INFO_BASE_DE_DADOS
    INFO_SERVER = configs.Server()
    INFO_BASE_DE_DADOS = base_de_dados.Base_de_Dados(app)
