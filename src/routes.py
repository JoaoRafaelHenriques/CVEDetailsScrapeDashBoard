from flask import Blueprint, render_template, request, jsonify
from modules.utils import calculo_diffs_diarios, consulta_base_de_dados, trata_categorias, trata_missing, trata_info_vulnerabidade, obter_id_projeto, testa_categoria

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
                Categoria (str): categorias
                Missing (str): missing
    """
    
    # Obtemos a informação dos parâmetro e transformamos tudo em tuplos
    projeto = request.args.get("Projeto").strip(" ").split(" & ")
    projeto.append(" ")
    if not projeto or "All" in projeto or "" in projeto:
        projeto = tuple(["", ""])
    else:
        projeto = tuple(projeto)
    categoria = request.args.get("Categoria").strip(" ").split(" & ")
    if not categoria or "All" in categoria or "" in categoria:
        categoria = tuple(["", ""])
        where_clause = ""
    else:
        categoria = tuple(categoria)
        
        # Contruímos uma condição para puder comparar todos os valores que nos foram passados
        where_clause = " OR " + " OR ".join([f"V_CLASSIFICATION LIKE '%{word}%'" for word in categoria])
        
    missing = request.args.get("Missing").strip(" ").split(" & ")
    missing.append(" ")
    if not missing or "Valid" in missing or "" in missing:
        missing = tuple(["", ""])
    else:
        missing = tuple(missing)
    offset = request.args.get("Page")
    size = 15
    if offset is None:
        offset = 0
    else:
        offset = (int(offset) - 1) * size

    print(where_clause)
    resultados = consulta_base_de_dados(f"""SELECT PROJECT, CVE, V_CLASSIFICATION, MISSING, VULNERABILITIES.V_ID
                                        FROM VULNERABILITIES 
                                        LEFT JOIN REPOSITORIES_SAMPLE ON VULNERABILITIES.R_ID = REPOSITORIES_SAMPLE.R_ID
                                        WHERE (PROJECT IN {projeto} OR "{projeto}" = "('', '')")
                                        AND ("{categoria}" = "('', '')" {where_clause})
                                        AND (MISSING IN {missing} OR "{missing}" = "('', '')");
                                        """)

    info = {"Resultados": [], "FiltrosProjetos": [], "FiltrosCategorias": [], "FiltrosMissing": [], "ValoresVulnerabilidade": [f"{offset + 1} to {offset + size}", len(resultados)]}
    resultados = resultados[offset : offset + size]
    
    infoProjetos = consulta_base_de_dados(f""" SELECT PROJECT FROM REPOSITORIES_SAMPLE;""")
    infoCategorias = consulta_base_de_dados(f""" SELECT DISTINCT(V_CLASSIFICATION) FROM VULNERABILITIES;""")
    infoMissing = consulta_base_de_dados(f""" SELECT DISTINCT(MISSING) FROM VULNERABILITIES;""")
    
    for linha in resultados:
        info["Resultados"].append([linha[1], trata_categorias(linha[2]), linha[0], trata_missing(linha[3]), linha[4]])
    for linha in infoProjetos:
        info["FiltrosProjetos"].append(linha[0])
    for linha in infoMissing:
        if linha[0] is None:
            continue
        info["FiltrosMissing"].append(linha[0])
    for linha in infoCategorias:
        help_ = trata_categorias(linha[0]).split(" | ")
        for cat in help_:
            if cat.title() not in info["FiltrosCategorias"]:
                info["FiltrosCategorias"].append(cat.title())
    return render_template("vulnerabilities_results.html", resultados=info)

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
    projeto = request.args.get("Projeto").strip(" ").split(" & ")
    projeto.append(" ")
    if not projeto or "All" in projeto or "" in projeto:
        projeto = tuple(["", ""])
    else:
        projeto = tuple(projeto)
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
                                        WHERE PROJECT IN {projeto} OR "{projeto}" = "('', '')"
                                        LIMIT {size}
                                        OFFSET {offset};""")

    info = {"Resultados": [], "FiltrosProjetos": []}
    
    infoProjetos = consulta_base_de_dados(f""" SELECT PROJECT FROM REPOSITORIES_SAMPLE;""")
    
    for linha in resultados:
        info["Resultados"].append([linha[1], linha[0]])
    for linha in infoProjetos:
        info["FiltrosProjetos"].append(linha[0])
        
    return render_template("patches_results.html", resultados=info)

@bp.route("/overview_cwes/", methods=["GET"])
def overview_cwes():
    """ Trata-se das cwes do dataset.
        São apresentadas todas as cwe, assim como o número de vezes que aparecem
        e algumas informações extra.
        
        Args:
            Dentro do request.args temos:
                CWE (str): cwe pesquisada
                Categoria (str): categorias a pesquisar

    """
    
    # Tentamos obter a cwe
    categoria = request.args.get("Categoria").strip(" ").split(" & ")
    categoria.append(" ")
    if not categoria or "All" in categoria or "" in categoria:
        categoria = tuple(["", ""])
    else:
        categoria = tuple(categoria)
    cwe = request.args.get("CWE")
    if cwe is None:
        cwe = ''
    offset = request.args.get("Page")
    size = 15
    if offset is None:
        offset = 0
    else:
        offset = (int(offset) - 1) * size
        
    # Procuramos a informação
    cwes = consulta_base_de_dados(f"""SELECT CWE_INFO.V_CWE, CWE_INFO.DESCRIPTION, VULNERABILITY_CATEGORY.NAME , COALESCE(counter.count, 0) as "contagem"
                                     FROM CWE_INFO 
                                     LEFT JOIN VULNERABILITY_CATEGORY 
                                     ON VULNERABILITY_CATEGORY.ID_CATEGORY = CWE_INFO.ID_CATEGORY 
                                     LEFT JOIN (SELECT V_CWE, COUNT(*) as count FROM VULNERABILITIES_CWE WHERE V_CWE = '{cwe}' OR '{cwe}' = '' GROUP BY V_CWE) AS counter ON CWE_INFO.V_CWE = counter.V_CWE
                                     WHERE (CWE_INFO.V_CWE = '{cwe}' OR '{cwe}' = '' )
                                     AND (VULNERABILITY_CATEGORY.NAME IN {categoria} OR "{categoria}" = "('', '')")
                                     ORDER BY contagem DESC
                                     LIMIT {size}
                                     OFFSET {offset};""")
    
    infoCategorias = consulta_base_de_dados(f"""SELECT DISTINCT(NAME) FROM VULNERABILITY_CATEGORY;""")
    
    dic: dict = {"CWES": {}, "FiltrosCategorias": []}

    # Adicionamos CWE ao numero para uma melhor leitura
    for linha in cwes:
        chave = linha[0]
        if "CWE-" + chave not in dic.keys():
            dic["CWES"]["CWE-" + chave] = [linha[3], linha[1], linha[2]]
    for linha in infoCategorias:
        dic["FiltrosCategorias"].append(linha[0])

    return render_template("cwes_results.html", resultados = dic)

@bp.route("/daily_update/")
def daily_update():
    """Obtemos a informação do último dia de atualizações.

    Returns:
        resultados: dicionário com a Data e Informação de cada projeto {DATA: DD-MM-YYY, INFO: {PROJETO: [0,0,0,0] ... }}
    """
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
    projeto = request.args.get("Projeto").strip(" ").split(" & ")
    projeto.append(" ")
    if not projeto or "All" in projeto or "" in projeto:
        lista_r_id = tuple(["", ""])
    else:
        projeto = tuple(projeto)
        
        lista_r_id = []
        for projeto_nome in projeto:
            lista_r_id.append(obter_id_projeto(projeto_nome))
        lista_r_id = tuple(lista_r_id)
    
    # Obter os valores
    vulnerabilidades = consulta_base_de_dados(f"""SELECT COUNT(*) FROM VULNERABILITIES WHERE R_ID IN {lista_r_id} OR "{lista_r_id}" = "('', '')";""")
    patches = consulta_base_de_dados(f"""SELECT COUNT(DISTINCT(P_COMMIT)) FROM PATCHES WHERE R_ID IN {lista_r_id} OR "{lista_r_id}" = "('', '')";""")
    cwes = consulta_base_de_dados(f"""SELECT COUNT(*) FROM CWE_INFO WHERE V_CWE IN (SELECT V_CWE FROM VULNERABILITIES_CWE WHERE V_ID IN (SELECT V_ID FROM VULNERABILITIES WHERE R_ID IN {lista_r_id})) OR "{lista_r_id}" = "('', '')";""")
    projetos = consulta_base_de_dados(f"""SELECT COUNT(*) FROM REPOSITORIES_SAMPLE WHERE R_ID IN {lista_r_id} OR "{lista_r_id}" = "('', '')";""")
    
    # Construir a lista de resultados
    dic: dict = {"FiltrosProjetos": []}
    dic_auxiliar: dict = {}

    dic_auxiliar["Vulnerabilities"] = vulnerabilidades[0][0]
    dic_auxiliar["Patches"] = patches[0][0]
    dic_auxiliar["CWEs"] = cwes[0][0]
    dic_auxiliar["Projects"] = projetos[0][0]
    dic['resultados'] = dic_auxiliar
    
    infoProjetos = consulta_base_de_dados(f""" SELECT PROJECT FROM REPOSITORIES_SAMPLE;""")
    
    for linha in infoProjetos:
        dic["FiltrosProjetos"].append(linha[0])
        
    return render_template("resume.html", resultados=dic)

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
    """ Route para a página de resumo da base de dados.
        Este endpoint apenas serve para recolher a informação do gráfico.
        
        Args:
            Dentro do request.args temos:
                Projeto (str): projeto usado na pesquisa
        Returns:
            Passamos em JSON:
                dic (dic|JSON): dicionário com todas as cwes mais comuns e a sua contagem por ano
    """
    
    # Obtemos a informação de um projeto
    projeto = request.args.get("Projeto").strip(" ").split(" & ")
    projeto.append(" ")
    if not projeto or "All" in projeto or "" in projeto:
        lista_r_id = tuple(["", ""])
    else:
        projeto = tuple(projeto)
        
        lista_r_id = []
        for projeto_nome in projeto:
            lista_r_id.append(obter_id_projeto(projeto_nome))
        lista_r_id = tuple(lista_r_id)
            
    dic: dict = {"Data": [], "Titulos": []}
    
    # Escolher as 5 mais comuns
    cwes_comuns = consulta_base_de_dados(f"""SELECT V_CWE, COUNT(*) 
                                         FROM VULNERABILITIES_CWE 
                                         LEFT JOIN VULNERABILITIES 
                                         ON VULNERABILITIES.V_ID = VULNERABILITIES_CWE.V_ID
                                         WHERE R_ID IN {lista_r_id} OR "{lista_r_id}" = "('', '')"
                                         GROUP BY VULNERABILITIES_CWE.V_CWE ORDER BY COUNT(*) DESC LIMIT 5;""");
    for cwe in cwes_comuns:
        dic["Titulos"].append([f'CWE-{str(cwe[0])}'])
        
    # Fazer a contagem para cada ano
    for cwe in dic["Titulos"]:
        info = consulta_base_de_dados(f"""SELECT CVE, V_CWE 
                                      FROM VULNERABILITIES 
                                      INNER JOIN VULNERABILITIES_CWE ON VULNERABILITIES_CWE.V_ID = VULNERABILITIES.V_ID 
                                      WHERE VULNERABILITIES_CWE.V_CWE = {cwe[0][4:]} AND (R_ID IN {lista_r_id} OR "{lista_r_id}" = "('', '')");""")
        info_tratada: dict = {
            '1999': 0, '2000': 0, '2001': 0, '2002': 0, '2003': 0, '2004': 0, '2005': 0, 
            '2006': 0, '2007': 0, '2008': 0, '2009': 0, '2010': 0, '2011': 0, '2012': 0,
            '2013': 0, '2014': 0, '2015': 0, '2016': 0, '2017': 0, '2018': 0, '2019': 0,
            '2020': 0, '2021': 0, '2022': 0, '2023': 0, '2024': 0
        }
        
        # Para cada linha adicionamos uma ocorrência em cada ano
        for linha in info:
            if linha[0] is None:
                continue
            cve = linha[0][4:8]
            info_tratada[cve] += 1
        
        dic["Data"].append(info_tratada)
    return jsonify(dic)