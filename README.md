# CVEDetailsScrapeDashBoard

Este dashboard oferece uma vista mais simples e prática sobre o dataset.
O dataset está disponível em:
- https://github.com/JoaoRafaelHenriques/CVEDetailsScrapeDataset

## Componentes

É possível aceder a vários detalhes do dataset:
1. Vulnerabilidades
2. Patches
3. Atualização Diária
4. CWEs
5. Resumo do Dataset

### Vulnerabilidades

Nesta aba podemos pesquisar por qualquer vulnerabilidade e obter as informações da mesma.
Ao aparecer a listagem de todas, podemos limitar a um projeto através da barra de pesquisa.
Ao clicar numa delas, obtemos mais informação sobre a mesma.

### Patches

Nesta aba podemos ver todos os patches e a que projeto pertencem.
Pode ser igualmente filtrado por projeto.

### Atualização Diária

Aqui é possível ver quais foram as mudanças na última atualização na base de dados.

### CWEs

Podemos ver todas as CWEs presentes assim como informação sobre as mesmas e a quantas vulnerabilidades estão ligadas.
Podem ser filtradas por número da CWE.

### Resumo do Dataset

Aqui podemos ver todas as informações do dataset.
Pode ser filtrado para um projeto apenas.

## Tecnologias

O software está construído em Python, usando Flask e flask_mysqldb.
O dataset está em MySQL e as informações presentes são atualizadas em tempo real.

