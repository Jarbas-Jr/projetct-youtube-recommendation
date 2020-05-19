from get_data import *
from ml_utils import *
import time

queries = ["machine+learning", "data+science", "kaggle"]

# A gente ta puxando essa função la pro arquivo python do app.
# Abre o arquivo novos videos, vai iterar pelas queries, que nem nos notebooks de coleta e processamento la no começo, entao e importante guardar para adapta-lo pra buscar as mesmas informações me produção.

def update_db():
    with open("novos_videos.json", 'w+') as output:
        for query in queries: 
            # aqui colocamos pra pegar até a pagina 3.
            for page in range(1,4):
                print(query, page)
                # a gente vai baixar a pagina de busca passando qual é a query e qual é a pagina. Retorna o codigo fonte e armazena esse search_page
                search_page = download_search_page(query, page)
                # mesma coisa pra pegar os links dos videos, so que ao invés de salvar em um dataframe que nem antes, a gente salva nesa video_list.
                video_list = parse_search_page(search_page)
                
                # e ai a gente vai iterar por cada video nessa video_list
                for video in video_list:
                        # baixar as informações da pagina do video, passando pra essa função o link do video, passando o link ela vai acessar essa pagina e buscar as informações, vai guardar na video_page, equivalente a aquela função que usavamos para salvar HTMLS, a pagina de cada video
                    video_page = download_video_page(video['link'])
                    # vamos fazer o processamento dessa pagina de video, e vamos retornar algumas informações como o json.
                    video_json_data = parse_video_page(video_page)
                    
                    # mario descobriu que alguns videos o endereço deles nao funcional, nao se acha as informações. Entao colocamos que se o 'watch-time-text' nao tiver no video_json_data, pula para o proximo video. Proteção pra nao travar.
                    if 'watch-time-text' not in video_json_data:
                        continue
                    # esse video_json_data, atraves da função compute_prediction, essa função vai pegar esses dados, criar as features, vai rodar o modelo e retornar pra gente a probabilidade de ser um video bom ou ruim. não probabilidade no sentido rigoroso mas um score de relevância pra gente rankear esses videos. 
                    p = compute_prediction(video_json_data)

                    # Essa basicamente é a parte que a gente fez com ML, daqui pra frente e so processamento desses dados pra jogar la pro fronted, a pagina onde tem a lista de videos.
                    
                    # aqui vou pegar uma 'tag', e vamos pegar o video_id que é o link do video.
                    video_id = video_json_data.get('og:video:url', '')
                    # e nesse data_front a gente passa as informações que a gente vai ter naquela lista de videos que criamos em app.py, quando rodamos o update.db, e das linhas criadas aqui individualmente. Com titulo, score e id do video.
                    data_front = {"title": video_json_data['watch-title'], "score": float(p), "video_id": video_id}
                    # momento em que a gente ta fazendo o processamento desse video no formato de nano segundos.
                    data_front['update_time'] = time.time_ns()
                    
                    # aqui e um print so pra questao de debuguing, so pra ver se ele ta processando tudo bem, mas a gente poderia comentar essa linha que nao faria muita diferença 
                    print(video_id, json.dumps(data_front))
                    
                    # depois ele joga tudo pro arquivo json, novos_videos.json, ele coloca um json por linha e esse vai ser nosso banco de dados dos ultimos videos que avaliamos. 
                    output.write("{}\n".format(json.dumps(data_front)))
    return True