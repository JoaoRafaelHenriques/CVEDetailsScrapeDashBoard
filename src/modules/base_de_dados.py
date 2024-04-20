import json
from typing import Any
from flask import Flask
from flask_mysqldb import MySQL

FILE = "modules/configs/configs.json"

class Base_de_Dados:
    
    host: str
    user: str
    password: str
    base_de_dados: str
    mysql: MySQL
        
    def __init__(self, app: Flask) -> None:
        configs = self.leitura_configs(FILE)
        for key, _ in configs.items():
            if key == 'base_de_dados':
                for key_bd, value_bd in configs[key].items():
                    setattr(self, key_bd, value_bd)
                self.inicializa_base_de_dados(app)    
                break
    
    def __repr__(self) -> str:
        """Retorna o que o objeto tem nos seus atributos.

        Returns:
            str: descrição do objeto.
        """
        return "Host: " + self.host + "\nUser: " + self.user + "\nPassword: " + self.password + "\nBase De Dados: " + self.base_de_dados
    
    def leitura_configs(self, caminho: str) -> dict:
        """Lê o ficheiro de configurações e retorna o dicionário do mesmo.

        Args:
            caminho (str): caminho do ficheiro

        Returns:
            dict: dicionário com as configurações
        """
        with open(caminho, "r") as file:
            configs = json.load(file)
        return configs
    
    def inicializa_base_de_dados(self, app: Flask) -> None:
        """Inicializa a base de dados.

        Args:
            app (Flask): aplicação criada
        """
        app.config['MYSQL_HOST'] = self.host
        app.config['MYSQL_USER'] = self.user
        app.config['MYSQL_PASSWORD'] = self.password
        app.config['MYSQL_DB'] = self.base_de_dados
        self.mysql = MySQL(app)
        
    def consulta(self, pesquisa: str) -> list:
        """Recebe uma consulta e retorna o resultado.

        Args:
            pesquisa (str): consulta que desejamos fazer
            
        Returns:
            list: lista de linhas sendo cada linha uma lista de colunas
        """
        cursor = self.mysql.connection.cursor()
        cursor.execute(pesquisa)
        resultados = [list(item) for item in cursor.fetchall()]
        cursor.close()
        return resultados
    
    def obter_id_projeto(self, projeto: str) -> int:
        """ Recebe o nome de um projeto e retorna o id do mesmo.
        
        Args:
            projeto (str): projeto
            
        Returns:
            int: id do projeto na base de dados
        """
        if projeto is None or projeto == "" or projeto == " ":
            return -1
        else:
            r_id = self.consulta(f"""SELECT R_ID FROM REPOSITORIES_SAMPLE WHERE PROJECT = '{projeto}';""")[0][0]
            return r_id
        
        
        
        
        
        
        
        
        
        
        