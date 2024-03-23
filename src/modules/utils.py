from flask import Flask
from . import configs, base_de_dados
from datetime import date, timedelta
import os

INFO_SERVER: configs.Server = None
INFO_BASE_DE_DADOS = None

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
            return len(file.readlines())
    return 0        

def calculo_diffs_diarios() -> dict:
    """Observa os valores de CVE para o último dia que foram coletadas.

    Returns:
        dict: dicionario com informação (atualizadas, desaparecidas, iguais, novas)
    """
    
    # Obtemos a data na forma YYYY-MM-DD
    data_hoje = date.today()
    data_ontem = data_hoje - timedelta(days = 1)
    
    info = dict()
    
    # Iteramos por todos os projetos
    for projeto in INFO_SERVER.projetos:
        
        # Testamos se já existe informação de hoje
        caminho = os.path.join(INFO_SERVER.diff_output, f"{projeto}_{data_hoje}")
        if not os.path.exists(caminho):
            caminho = os.path.join(INFO_SERVER.diff_output, f"{projeto}_{data_ontem}")
        
        # Dicionario com a informação (atualizadas, desaparecidas, iguais, novas)
        info[projeto] = []
        for tipo in sorted(os.listdir(caminho)):
            
            # Queremos ignorar qualquer coisa que não seja os diffs
            if projeto in tipo:
                caminho_tipo = os.path.join(caminho, tipo)
                info[projeto].append(leitura_ficheiro(caminho_tipo))
 
    return info

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
