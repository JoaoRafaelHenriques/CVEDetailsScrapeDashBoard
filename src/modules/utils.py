from flask import Flask
from . import configs, base_de_dados
from datetime import date, timedelta
import os

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
        return "Válido"
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
        dict: dicionario com informação (atualizadas, desaparecidas, iguais, novas)
        data: data do dia em que foi feito o cálculo
    """
    
    # Obtemos a data na forma YYYY-MM-DD
    data_hoje = date.today()
    
    info = dict()
    
    # Iteramos por todos os projetos
    for projeto in INFO_SERVER.projetos:
        
        # Testamos se já existe informação de hoje
        caminho = os.path.join(INFO_SERVER.diff_output, f"{projeto}_{data_hoje}")
        while not os.path.exists(caminho):
            data_hoje = data_hoje - timedelta(days = 1)
            caminho = os.path.join(INFO_SERVER.diff_output, f"{projeto}_{data_hoje}")
        
        # Dicionario com a informação (atualizadas, desaparecidas, iguais, novas)
        info[projeto] = []
        for tipo in sorted(os.listdir(caminho)):
            
            # Queremos ignorar qualquer coisa que não seja os diffs
            if projeto in tipo:
                caminho_tipo = os.path.join(caminho, tipo)
                info[projeto].append(leitura_ficheiro(caminho_tipo))
    
    return info, data_hoje

def obter_id_projeto(projeto: str) -> int:
    """Obtém o id do projeto através do seu nome.

    Args:
        projeto (str): projeto

    Returns:
        int: id do projeto
    """
    return INFO_BASE_DE_DADOS.obter_id_projeto(projeto)

def consulta_base_de_dados(pesquisa: str) -> list:
    """Faz uma pesquisa na base de dados e retorna a lista de resultados.

    Args:
        pesquisa (str): consulta desejada

    Returns:
        list: lista de linhas e colunas pedidas
    """
    return INFO_BASE_DE_DADOS.consulta(pesquisa)

def inicializa(app: Flask):
    """Inicializa as variáveis INFO_SERVER, INFO_BASE_DE_DADOS para serem usadas nas restantes
    funções.

    Args:
        app (Flask): aplicação Flask
    """
    global INFO_SERVER, INFO_BASE_DE_DADOS
    INFO_SERVER = configs.Server()
    INFO_BASE_DE_DADOS = base_de_dados.Base_de_Dados(app)
