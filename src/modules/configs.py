import json
import os

FILE = "modules/configs/configs.json"

class Server:
    
    output: str
    diff_output: str
    projetos: list
        
    def __init__(self) -> None:
        print(os.path.abspath(FILE))
        configs = self.leitura_configs(FILE)
        for key, value in configs.items():
            setattr(self, key, value)
    
    def __repr__(self) -> str:
        """Retorna o que o objeto tem nos seus atributos.

        Returns:
            str: descrição do objeto.
        """
        return "Output: " + self.output + "\nDiff output: " + self.diff_output + "\nProjetos: " + str(self.projetos)

    def leitura_configs(self, caminho: str) -> dict:
        """Lê o ficheiro de configurações e retorna o dicionário do mesmo.

        Args:
            caminho (str): caminho do ficheiro

        Returns:
            dict: dicionário com as configurações
        """
        with open(caminho, "r") as file:
            return json.load(file)