from flask import Blueprint, render_template, request, jsonify
from modules.utils import calculo_diffs_diarios, consulta_base_de_dados, trata_categorias, trata_missing, trata_info_vulnerabidade

bp = Blueprint("pages", __name__)

@bp.route("/")
def home():
    """Página inicial do dashboard.
       Renderiza o HTML sem qualquer tipo de parâmetro.
    """
    return render_template('home.html')

@bp.route("/overview_vulnerabilities/", methods =["GET"])
def overview_vulnerabilities():
    """ Route para a página de vulnerabilidades.

        Args:
            Dentro do request.args temos:
                Page (str): página
                Projeto (str): projeto
    """
    
    # Obtemos a informação dos parâmetros
    projeto = request.args.get("Projeto")
    offset = request.args.get("Page")
    size = 15
    if offset is None:
        offset = 0
    else:
        offset = (int(offset) - 1) * size
    resultados = consulta_base_de_dados(f"""SELECT PROJECT, CVE, V_CLASSIFICATION, MISSING, VULNERABILITIES.V_ID
                                        FROM VULNERABILITIES 
                                        LEFT JOIN REPOSITORIES_SAMPLE ON VULNERABILITIES.R_ID = REPOSITORIES_SAMPLE.R_ID
                                        WHERE PROJECT = '{projeto}' OR '{projeto}' = ''
                                        LIMIT {size}
                                        OFFSET {offset};""")
    lista = list()
    for linha in resultados:
        lista.append([linha[1], trata_categorias(linha[2]), linha[0], trata_missing(linha[3]), linha[4]])
    return render_template("vulnerabilities_results.html", resultados=lista)

@bp.route("/overview_patches/", methods =["GET"])
def overview_patches():
    """ Tratamos dos patches.
        Pode ser feita a pesquisa de todos ou por projeto.
        
        Args:
            Dentro do request.args temos:
                Projeto (str): projeto usado na pesquisa
                Page (str): página
    """
    
    # Procuramos o projeto e a página a ser utilizados
    projeto = request.args.get("Projeto")
    offset = request.args.get("Page")
    size = 15
    if offset is None:
        offset = 0
    else:
        offset = (int(offset) - 1) * size
        
    # Obtemos a informação geral da base de dados sobre patches
    resultados = consulta_base_de_dados(f"""SELECT DISTINCT(P_COMMIT), PROJECT
                                        FROM PATCHES 
                                        LEFT JOIN REPOSITORIES_SAMPLE ON PATCHES.R_ID = REPOSITORIES_SAMPLE.R_ID
                                        WHERE PROJECT = '{projeto}' OR '{projeto}' = ''
                                        LIMIT {size}
                                        OFFSET {offset};""")
    lista = list()
    for linha in resultados:
        lista.append([linha[1], linha[0]])
    return render_template("patches_results.html", resultados=lista)

@bp.route("/overview_cwes/", methods=["GET"])
def overview_cwes():
    """ Trata-se das cwes do dataset.
        São apresentadas todas as cwe, assim como o número de vezes que aparecem
        e algumas informações extra.
        
        Args:
            Dentro do request.args temos:
                CWE (str): cwe pesquisada

    """
    
    # Tentamos obter a cwe
    cwe = request.args.get("CWE")
    if cwe is None:
        cwe = ''
        
    # Procuramos a informação
    cwes = consulta_base_de_dados(f"""SELECT V_CWE, DESCRIPTION, NAME 
                                     FROM CWE_INFO 
                                     LEFT JOIN VULNERABILITY_CATEGORY 
                                     ON VULNERABILITY_CATEGORY.ID_CATEGORY = CWE_INFO.ID_CATEGORY 
                                     WHERE CWE_INFO.V_CWE = '{cwe}' OR '{cwe}' = '';""")
    counter = consulta_base_de_dados(f"""SELECT V_CWE, COUNT(*) 
                                     FROM VULNERABILITIES_CWE 
                                     WHERE V_CWE = '{cwe}' OR '{cwe}' = '' 
                                     GROUP BY V_CWE;""")
    
    # Construimos os resultados com o que obtivemos
    dic: dict = {}
    for linha in counter:
        dic["CWE-" + linha[0]] = linha[1]

    for linha in cwes:
        chave = linha[0]
        if "CWE-" + chave not in dic.keys():
            dic["CWE-" + chave] = [0, linha[1], linha[2]]
        else:
            dic["CWE-" + chave] = [dic["CWE-" + chave], linha[1], linha[2]]
    return render_template("cwes_results.html", resultados = dic)

@bp.route("/daily_update/")
def daily_update():
    
    # Obtemos toda a informação do dia mais atualizado possivel
    # Ordem alfabética, atualizadas, desaparecidas, iguais, novas
    info, data = calculo_diffs_diarios()
    dic: dict = {"Data": [str(data)], "Info": info}

    return render_template("daily_update.html", resultados = dic)

@bp.route("/resumeflask/", methods=["GET"])
def resumeflask():
    """ Route para a página de resumo da base de dados.
        Obtemos informação geral sobre o que se passa na mesma.
        
        Args:
            Dentro do request.args temos:
                Projeto (str): projeto usado na pesquisa
    """
    
    # Tentamos identificar o projeto, se não conseguirmos usamos todos
    projeto = request.args.get("Projeto")
    if projeto is None:
        projeto = ""
        r_id = -1
    else:
        try:
            r_id = consulta_base_de_dados(f"""SELECT R_ID FROM REPOSITORIES_SAMPLE WHERE PROJECT = '{projeto}';""")[0][0]
        except Exception as error:
            print(error)
            projeto = ""
            r_id = -1
            
    # Obter os valores
    vulnerabilidades = consulta_base_de_dados(f"""SELECT COUNT(DISTINCT(CVE)) FROM VULNERABILITIES WHERE R_ID = {r_id} OR '{projeto}' = '';""")
    patches = consulta_base_de_dados(f"""SELECT COUNT(DISTINCT(P_COMMIT)) FROM PATCHES WHERE R_ID = {r_id} OR '{projeto}' = '';""")
    cwes = consulta_base_de_dados(f"""SELECT COUNT(*) FROM CWE_INFO WHERE V_CWE IN (SELECT V_CWE FROM VULNERABILITIES_CWE WHERE V_ID IN (SELECT V_ID FROM VULNERABILITIES WHERE R_ID = {r_id})) OR '{projeto}' = '';""")
    projetos = consulta_base_de_dados(f"""SELECT COUNT(*) FROM REPOSITORIES_SAMPLE WHERE R_ID = {r_id} OR '{projeto}' = '';""")
    
    # Construir a lista de resultados
    dic: dict = {}
    dic_auxiliar: dict = {}

    dic_auxiliar["Vulnerabilidades"] = vulnerabilidades[0][0]
    dic_auxiliar["Patches"] = patches[0][0]
    dic_auxiliar["CWEs"] = cwes[0][0]
    dic_auxiliar["Projetos"] = projetos[0][0]
    dic['resultados'] = dic_auxiliar
        
    return render_template("resume.html", results=dic)

@bp.route("/overview_vulnerability/", methods=["GET"])
def overview_vulnerability():
    """ Route onde se mostra toda a informação sorbe uma determinada vulnerabilidade referenciada pelo seu id na base de dados.

        Args:
            Dentro do request.args temos:
                id (str): id da vulnerabilidade
    """
    
    # Lemos o id e passamos para inteiro
    v_id = int(request.args.get("id"))

    # Obtemos toda a informação com atenção para o caso de não haver cwes
    info = consulta_base_de_dados(f"""SELECT CVE, V_CLASSIFICATION, VULNERABILITY_URL, MISSING, PROJECT FROM VULNERABILITIES LEFT JOIN REPOSITORIES_SAMPLE ON REPOSITORIES_SAMPLE.R_ID = VULNERABILITIES.R_ID WHERE V_ID = {v_id};""")
    info2 = consulta_base_de_dados(f"""SELECT P_URL, P_COMMIT FROM PATCHES WHERE V_ID = {v_id};""")
    info3 = consulta_base_de_dados(f"""SELECT VULNERABILITIES_CWE.V_CWE, DESCRIPTION, ID_CATEGORY FROM VULNERABILITIES_CWE LEFT JOIN CWE_INFO ON CWE_INFO.V_CWE = VULNERABILITIES_CWE.V_CWE WHERE V_ID = {v_id};""")
    if len(info3) > 0:
        info4 = consulta_base_de_dados(f"""SELECT NAME FROM VULNERABILITY_CATEGORY WHERE ID_CATEGORY = {info3[0][2]};""")
    else:
        info4: list = []    
    info5 = consulta_base_de_dados(f"""SELECT * FROM VETORES WHERE V_ID = {v_id};""")
    
    dic: dict = {"Vulnerabilidades": [], "Patches": [], "CWE": [], "Categoria": [], "Vetores": []}
    for linha in info:
        dic["Vulnerabilidades"].append([linha[0], trata_categorias(linha[1]), linha[2], trata_missing(linha[3]), linha[4]])
    for linha in info2:
        dic["Patches"].append([linha[0], linha[1]])
    for linha in info3:
        dic["CWE"].append([linha[0], linha[1]])
    for linha in info4:
        dic["Categoria"].append([linha[0]])
    for linha in info5:
        dic["Vetores"].append([linha[0], linha[1], linha[2], linha[3], linha[4], linha[5], linha[6], linha[7], linha[8], linha[9], linha[10], linha[11], linha[12], linha[14], linha[15], linha[16], linha[17], linha[18]])
    
    # Removemos os Nones do dicionário
    dic = trata_info_vulnerabidade(dic)
    
    return render_template("overview_vulnerability.html", resultados = dic)

@bp.route("/grafico/", methods=["GET"])
def grafico():
    
    projeto = request.args.get("Projeto")
    if projeto is None:
        projeto = ""
        r_id = -1
        print("Aqui")
    else:
        try:
            r_id = consulta_base_de_dados(f"""SELECT R_ID FROM REPOSITORIES_SAMPLE WHERE PROJECT = '{projeto}';""")[0][0]
        except Exception as error:
            print(error)
            projeto = ""
            r_id = -1
            
    dic: dict = {"Data": [], "Titulos": []}
    
    # Escolher as 5 mais comuns
    cwes_comuns = consulta_base_de_dados(f"""SELECT V_CWE, COUNT(*) 
                                         FROM VULNERABILITIES_CWE 
                                         LEFT JOIN VULNERABILITIES 
                                         ON VULNERABILITIES.V_ID = VULNERABILITIES_CWE.V_ID
                                         WHERE R_ID = {r_id} OR '{projeto}' = ""
                                         GROUP BY VULNERABILITIES_CWE.V_CWE ORDER BY COUNT(*) DESC LIMIT 5;""");
    for cwe in cwes_comuns:
        dic["Titulos"].append([f'CWE-{str(cwe[0])}'])
        
    # Fazer a contagem para cada ano
    for cwe in dic["Titulos"]:
        info = consulta_base_de_dados(f"""SELECT CVE, V_CWE 
                                      FROM VULNERABILITIES 
                                      INNER JOIN VULNERABILITIES_CWE ON VULNERABILITIES_CWE.V_ID = VULNERABILITIES.V_ID 
                                      WHERE VULNERABILITIES_CWE.V_CWE = {cwe[0][4:]} AND (R_ID = {r_id} OR '{projeto}' = "");""")
        info_tratada: dict = {
            '1999': [], '2000': [], '2001': [], '2002': [], '2003': [], '2004': [], '2005': [], 
            '2006': [], '2007': [], '2008': [], '2009': [], '2010': [], '2011': [], '2012': [],
            '2013': [], '2014': [], '2015': [], '2016': [], '2017': [], '2018': [], '2019': [],
            '2020': [], '2021': [], '2022': [], '2023': [], '2024': []
        }
        for linha in info:
            if linha[0] is None:
                continue
            cve = linha[0][4:8]
            info_tratada[cve].append(linha[1])
        
        for c, v in info_tratada.items():
            info_tratada[c] = len(v)
        
        dic["Data"].append(info_tratada)
    return jsonify(dic)