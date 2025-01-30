import pandas as pd
from sklearn.neighbors import NearestNeighbors
from botcity.maestro import *

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

def train_model() -> tuple:
    try:
        # Carregar os dados
        notas = pd.read_csv('ratings.csv', encoding='latin-1')
        filmes = pd.read_csv('movies.csv', encoding='latin-1')
        notas.columns = ['userId', 'movieId', 'rating']
    except Exception as e:
        print(f"Erro ao carregar os arquivos CSV: {e}")
        return None, None, None

    # Criar uma matriz de user-filme
    matriz_usuario_filme = notas.pivot(index='userId', columns='movieId', values='rating').fillna(0)
    
    # Treinar o modelo KNN
    modelo_knn = NearestNeighbors(metric='cosine', algorithm='brute')
    modelo_knn.fit(matriz_usuario_filme.values)

    return modelo_knn, matriz_usuario_filme, filmes

# Função para recomendar filmes
def recomendar_filmes(user_id: int, modelo_knn: NearestNeighbors, matriz_usuario_filme: pd.DataFrame, filmes: pd.DataFrame, n_recomendacoes: int = 5) -> list:
    distancias, indices = modelo_knn.kneighbors(matriz_usuario_filme.loc[user_id, :].values.reshape(1, -1), n_neighbors=n_recomendacoes + 1)
    indices = indices.flatten()
    distancias = distancias.flatten()
    
    recomendacoes = []
    for i in range(1, len(indices)):
        filme_id = matriz_usuario_filme.columns[indices[i]]
        filme_titulo = filmes[filmes['movieId'] == filme_id]['title'].values[0]
        recomendacoes.append(filme_titulo)
    
    return recomendacoes

def main():
    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()

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

    modelo_knn, matriz_usuario_filme, filmes = train_model()
    if modelo_knn is None:
        print("Erro ao treinar o modelo. Verifique os arquivos CSV.")
        return

    while datapool.has_next():
        # Buscar o próximo item do Datapool
        item = datapool.next(task_id=execution.task_id)
        if item is None:
            # O item pode ser None se outro processo o consumiu antes
            maestro.alert(
                task_id=execution.task_id,
                title="INFO [Bot Recomendações]",
                message="NÃO HÁ DADOS PARA PROCESSAR",
                alert_type=AlertType.INFO
            )
            break

        try:
            user_id = int(item['user_id'])
            recomendacoes = recomendar_filmes(user_id, modelo_knn, matriz_usuario_filme, filmes)

            arquivo_filmes = f"{item['email']}-filmes-recomendados.txt"
            with open(arquivo_filmes, "w") as arquivo:
                for movie in recomendacoes:
                    arquivo.write(movie + "\n")

            print(f"Recomendações de filmes para o user {user_id}:")
            for titulo in recomendacoes:
                print(f"{titulo}")

            maestro.post_artifact(
                task_id=execution.task_id,
                artifact_name=arquivo_filmes,
                filepath=arquivo_filmes
            )

            item.report_done()
            processed_items += 1

        except Exception as e:
            items_with_error += 1
            message = f"Não foi possível processar as recomendações para o usuário {user_id}. ERRO: {e}"
            maestro.error(task_id=execution.task_id, exception=message)

    if items_with_error > 0:
        maestro.finish_task(
            task_id=execution.task_id,
            status=AutomationTaskFinishStatus.PARTIALLY_COMPLETED,
            message="Task Finished with items with error.",
            total_items=processed_items + items_with_error,
            processed_items=processed_items,
            failed_items=items_with_error
        )
    else:
        maestro.finish_task(
            task_id=execution.task_id,
            status=AutomationTaskFinishStatus.SUCCESS,
            message="Task Finished with SUCCESS.",
            total_items=processed_items + items_with_error,
            processed_items=processed_items,
            failed_items=items_with_error
        )
    
    maestro.alert(
        task_id=execution.task_id,
        title="INFO [Bot Recomendações]",
        message="BOT FINALIZOU TAREFA",
        alert_type=AlertType.INFO
    )

if __name__ == '__main__':
    main()