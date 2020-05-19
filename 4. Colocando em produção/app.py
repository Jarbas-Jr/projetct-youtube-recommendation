# deploy_front/app.py


import os.path
from flask import Flask
import os
import json
import run_backend

import time

# criando esse app, pra criar o objeto flask pra que ele sirva as paginas pro servidor entender os comandos que ele vai receber.
app = Flask(__name__)


# Pode-se escolher um banco de dados mais sofisticados como SQlite ou seila, mas nesse caso pra deixar as coisas simples e claras, vamos usar um arquivo como banco de dados, como nao e o caso de precisar de senha, nao sao dados sigiliosos e tal, a gente pode colocar tudo num arquivo que nao da nada, é um prototipo, um arquivo bem simples.

# Primeiro crio uma lista pra ele armazena os videos novos com as previsões.

# crio esse arquivo "novos_videos.json", entao coloco: se não existir, se o arquivo que eu passei aqui nessa variavel nao existir, ele vai rodar uma função update.db que vai estar no run_backend e vai puxar esses videos pra gente e colocar nesse arquivo.

# abrindo o arquivo "novos_videos.json", ele vai ter um json por linha e em cada um, o titulo, score(previsão do ensemble), e o video id que é o link para o video. E o uptade time, que é o horario que pegamos o video la do YT. Lista simples de varios json's.

# Para pegar o last_update, usamos a função getmtime, que pega o momento em que o arquivo foi modificado pela ultima vez, e ele vai retornar isso em segundos desde 01-01-1970, e mario multiplica por 1e9, pq ele usa a unidade em nano segundos, ja que ele nos retorna em unidade de segundos, nao e necessario mas mario prefere usar em nano segundo.

# depois tem um 'if': se o momento atual, quando alguem fez a requisição dessa pagina menos(-) for maior que 720 horas, ele vai falar: se faz mais de um mês, FAÇA A ATUALIZAÇÃO DO BANCO DE DADOS. Que é através do update_db. 

# PQ UM MÊS ? Nem toda semana ou mês vao ter videos interessantes, entao e desnecessario atualizar com uma frequencia maior. Poderia ser até mais que um mês, mas vamos deixar assim.

# Na parte do 'with open' ja temos o arquivo salvo no disco do servidor, agora vamos ler esse arquivo, pegar cada json e colocar naquela lista videos criada no inicio da função.

# Agora vamos iterar pela lista de videos e criar outra lista, a de previsões. Pq isso? Pq eu nao quero que ele me mostre todos os videos, ficaria uma pagina muito grande. Vou usar a função sorted pra ele poder rankear do video mais interessante pro menos interessante e so retornar pra mim os 30 mais interessantes. 
def get_predictions():

    videos = []
    
    novos_videos_json = "novos_videos.json"
    if not os.path.exists(novos_videos_json):
        run_backend.update_db()
    
    last_update = os.path.getmtime(novos_videos_json) * 1e9

    #if time.time_ns() - last_update > (720*3600*1e9): # aprox. 1 mes
    #    run_backend.update_db()

    with open("novos_videos.json", 'r') as data_file:
        for line in data_file:
            line_json = json.loads(line)
            videos.append(line_json)

    predictions = []
    for video in videos:
        # depois que cria a lista de tuples
        predictions.append((video['video_id'], video['title'], float(video['score'])))
    # aplico a função sorted, usar a função no key, vai pegar o ultimo elemento(score) e vai ordenar de trás pra frente, do maior pro menor essa lista, e vou pegar o 30 primeiros
    predictions = sorted(predictions, key=lambda x: x[2], reverse=True)[:30]

    # agora vou iterar, so que ppr essa lista. E nessa lista vou colcoar o código HTML pra cada um dos videos que estão nessa lista de predictions, temos um HTML muito simples que criar uma tag com hiperlink pra cada video, e coloca nessas th e tr que são as tags pra organizar a tabela, e coloca a score tbm. Isso é o codigo de cada um dos videos que temos na pagina do app. 
    predictions_formatted = []
    for e in predictions:
        #print(e)
        predictions_formatted.append("<tr><th><a href=\"{link}\">{title}</a></th><th>{score}</th></tr>".format(title=e[1], link=e[0], score=e[2]))
  
    # no fim eu preciso dar um 'join' nessa lista e colocar uma linha, eu coloco cada item dessa lista numa nova linha pra ele formatar corretamente a tabela. É possivel ver isso mais claro no codigo fonte da pagina do app.
     # Daqui o get_prediction vai pro main_page e o resto ta explicado la.
    return '\n'.join(predictions_formatted), last_update



# Pra indicar pro flask pra onde ele tem que indicar uma requisição, temos que usar o 'decorator' do python, nao precisa entender mas é uma função que colocamos com "@", ela vai pegar a função abaixo, no caso main_page, e vai aceita-la como argumento pra poder fazer alguns processos internos. Dentro do parenteses temos que colocar qual vai ser a requisição que vai chamar essa função "('/')", então o que estamos falando é: quando fizerem a requisição pra '/', pro diretorio raiz do nosso dominio, aplicação, retornamos o resultado dessa função. Quando acessarmos o endereço passado do heroku onde o app está hospedado, vamos receber o resultado dessa função.

# Essa função faz basicamente duas coisa: ela vai rodar a função get_predictions e vai receber as previsões relativamente formatas e o momento em que foi rodado o 'last_update', o momento em que ele buscou pela ultima vez os videos no YT. Pq? Pq precisamos ir la no YT buscar os videos novos que foram postados pra gente fazer as previsões e eu quero guardar esse las_update pra guardar aqui na pagina quando retornar.
@app.route('/')
# Ao rodar essa função ele está retornando uma string com código HTML e um cabeçallho com "Recomendador de Vídeos do Youtube", e ai no corpo ele coloca os segundos desde a ultima atualização, através do last_update. E na tabela ele vai colocar o pred que é uma string muuuito grande, onde ele coloca cada video dentro de uma tabela pra ficar razoalvemente formatada. Coloca o titulo, o score que o modelo de ensemble deu pra esse video, e tambem o link que nos leva para o video.  
def main_page():
    preds, last_update = get_predictions()
    return """<head><h1>Recomendador de Vídeos do Youtube</h1></head>
    <body>
    Segundos desde a última atualização: {}
    <table>
             {}
    </table>
    </body>""".format((time.time_ns() - last_update) / 1e9, preds)

# pro flask rodar precisamos colcoar isso "if __name__ == '__main__':" que é coisa comum do python pra rodar scripts, e em geral para apps de produção nao se coloca debug=True se nao vai ficar debugando ele. E o host que é o ip dentro da maquina onde vai rodar essa aplicação.
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')