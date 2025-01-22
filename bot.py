import pandas as pd

import pandas as pd
from sklearn.neighbors import NearestNeighbors

from botcity.maestro import *

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

def main():

    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()

    ## Fetch the BotExecution with details from the task, including parameters
    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")


    # Consumindo o próximo item disponível e reportando o estado de finalização ao final
    datapool = maestro.get_datapool(label="recomenda-filmes")
    maestro.alert(
        task_id=execution.task_id,
        title="INFO [Bot Recomendações]",
        message="BOT INICIOU TAREFA",
        alert_type=AlertType.INFO
    )

    processed_items = 0
    items_with_error = 0

    while datapool.has_next():
        # Buscar o próximo item do Datapool
        item = datapool.next(task_id=execution.task_id)
        if item is None:
            # O item pode ser None se outro processo o consumiu antes
            maestro.alert(
                task_id=execution.task_id,
                title="INFO [Bot Recomendações]",
                message= "NÃO HÁ DADOS PARA PROCESSAR",
                alert_type=AlertType.INFO
            )
            break

        # Carregar os dados
        notas = pd.read_csv('ratings.csv', encoding='latin-1')
        filmes = pd.read_csv('movies.csv',  encoding='latin-1')
        notas.colums = ['userId', 'movieId', 'rating']

        # Criar uma matriz de user-filme
        matriz_usuario_filme = notas.pivot(index='userId', columns='movieId', values='rating').fillna(0)
        # Treinar o modelo KNN
        modelo_knn = NearestNeighbors(metric='cosine', algorithm='brute')
        modelo_knn.fit(matriz_usuario_filme.values)

        # Funcao para recomendar filmes
        def recomendar_filmes(user_id, n_recomendacoes=5):
            distancias, indices = modelo_knn.kneighbors(matriz_usuario_filme.loc[user_id, :].values.reshape(1, -1), n_neighbors=n_recomendacoes+1)
            indices = indices.flatten()
            distancias = distancias.flatten()
            
            recomendacoes = []
            for i in range(1, len(indices)):
                filme_id = matriz_usuario_filme.columns[indices[i]]
                filme_titulo = filmes[filmes['movieId'] == filme_id]['title'].values[0]
                recomendacoes.append((filme_titulo, distancias[i]))
            
            return recomendacoes


        try:
            user_id = int(item['user_id'])
            recomendacoes = recomendar_filmes(user_id)
            print(f"Recomendacoes de filmes para o user {user_id}:")
            for titulo in recomendacoes:
                print(f"{titulo}")

            item.report_done()
            processed_items += 1

        except Exception as e:
            items_with_error += 1
            message = f"Não foi possível processar o as recomendações para o usuário {user_id}. ERRO: {e}"
            maestro.error(task_id=execution.task_id, exception=message)


    if items_with_error > 0:
        maestro.finish_task(
            task_id=execution.task_id,
            status=AutomationTaskFinishStatus.PARTIALLY_COMPLETED,
            message=f"Task Finished with items with error.",
            total_items= processed_items+items_with_error,
            processed_items= processed_items,
            failed_items= items_with_error
        )

    else:
        maestro.finish_task(
            task_id=execution.task_id,
            status=AutomationTaskFinishStatus.SUCCESS,
            message="Task Finished with SUCCESS.",
            total_items= processed_items+items_with_error,
            processed_items= processed_items,
            failed_items= items_with_error
        )


if __name__ == '__main__':
    main()

    