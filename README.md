# botMovies: Recomendando filmes de forma escalável utilizando BotCity.

### Este projeto implementa um bot que recomenda filmes para usuários com base em suas avaliações anteriores. O bot utiliza a biblioteca scikit-learn para treinar um modelo de K-Nearest Neighbors (KNN) e a biblioteca BotCity Maestro para gerenciar a execução das tarefas.

## Requisitos:

- Python 3.9+

- Pandas

- Scikit-learn

- BotCity Maestro SDK

## Instalação:

- Clone o repositório:

```
git clone https://github.com/seu-usuario/bot-recomendacoes-filmes.git
cd bot-recomendacoes-filmes
```

- Instale as dependências:

```pip install -r requirements.txt```


#### Certifique-se de ter os arquivos ratings.csv e movies.csv no diretório do projeto. Estes arquivos devem conter as avaliações dos usuários e os detalhes dos filmes, respectivamente.

## Estrutura do Código

- Importações: Importa as bibliotecas necessárias (pandas, scikit-learn e BotCity Maestro).

- Função main: Configura a conexão com o BotCity Maestro, obtém a execução da tarefa e consome itens do datapool.

- Carregamento de Dados: Carrega os dados de avaliações e filmes a partir de arquivos CSV.

- Treinamento do Modelo: Cria uma matriz de usuário-filme e treina um modelo KNN usando a métrica de cosseno.

- Função recomendar_filmes: Recomenda filmes para um usuário específico com base nas avaliações anteriores.

- Processamento de Itens: Processa cada item do datapool, gera recomendações e reporta o estado da tarefa ao BotCity Maestro.

## Exemplo de Saída

```
Task ID is: 12345
Task Parameters are: {'param1': 'value1'}
Recomendacoes de filmes para o user 1:
('Filme A', 0.1)
('Filme B', 0.2)
('Filme C', 0.3)
('Filme D', 0.4)
('Filme E', 0.5)
```
