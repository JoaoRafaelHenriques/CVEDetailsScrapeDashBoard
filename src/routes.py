from flask import Blueprint, render_template, request
from modules.utils import calculo_diffs_diarios, consulta_base_de_dados, trata_categorias, trata_missing

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
    # kernel linux, elastic search, apache cassandra e os restantes são normais

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

@bp.route("/overview_cwes")
def overview_cwes():
    # Obtemos a informação geral da base de dados sobre cwes
    resultados = consulta_base_de_dados("""SELECT V_CWE, COUNT(*) 
                                        FROM VULNERABILITIES_CWE 
                                        GROUP BY V_CWE;""")
    string: str = ""
    for linha in resultados:
        string += f"CWE-{linha[0]}: {linha[1]} times\n"
    return string

@bp.route("/daily_update")
def daily_update():
    # Obtemos toda a informação do dia mais atualizado possivel
    # Ordem alfabética, atualizadas, desaparecidas, iguais, novas
    info = calculo_diffs_diarios()
    string: str = ''
    for key, value in info.items():
        string += key
        for num in value:
            string += '\n\t' + str(num)
        string += '\n'
    return string

@bp.route("/resumeflask")
def resumeflask():
    """ Route para a página de resumo da base de dados.
        Obtemos informação geral sobre o que se passa na mesma.
    """
    
    # Obter os valores
    vulnerabilidades = consulta_base_de_dados("""SELECT COUNT(DISTINCT(CVE)) FROM VULNERABILITIES;""")
    patches = consulta_base_de_dados("""SELECT COUNT(DISTINCT(P_COMMIT)) FROM PATCHES;""")
    cwes = consulta_base_de_dados("""SELECT COUNT(*) FROM CWE_INFO;""")
    projetos = consulta_base_de_dados("""SELECT COUNT(*) FROM REPOSITORIES_SAMPLE;""")
    
    # Construir a lista de resultados
    lista = list()
    lista.append(["Vulnerabilidades", vulnerabilidades[0][0]])
    lista.append(["Patches", patches[0][0]])
    lista.append(["CWEs", cwes[0][0]])
    lista.append(["Projetos", projetos[0][0]])
    return render_template("resume.html", resultados=lista)


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
    dic: dict = {"Vulnerabilidades": [], "Patches": [], "CWE": [], "Categoria": []}
    for linha in info:
        dic["Vulnerabilidades"].append([linha[0], trata_categorias(linha[1]), linha[2], trata_missing(linha[3]), linha[4]])
    for linha in info2:
        dic["Patches"].append([linha[0], linha[1]])
    for linha in info3:
        dic["CWE"].append([linha[0], linha[1]])
    for linha in info4:
        dic["Categoria"].append([linha[0]])
    return render_template("overview_vulnerability.html", resultados = dic)