import pandas as pd
import re
import joblib as jb
from scipy.sparse import hstack, csr_matrix
import numpy as np
import json

# Aqui vamos ver muita coisa que também não será novidade.

# processar as datas da mesma maneira que fizemos na coleta de dados
mapa_meses = {"jan": "Jan",
            "fev": "Feb",
            "mar": "Mar", 
            "abr": "Apr", 
            "mai": "May", 
            "jun": "Jun",
            "jul": "Jul",
            "ago": "Aug", 
            "set": "Sep", 
            "out": "Oct", 
            "nov": "Nov",
            "dez": "Dec"}


# aqui temos uma diferença, aqui carregamos os modelos, no formato pkl.z, seria a mesma coisa que estivessemos treinando e fazendo as previsões do modelo aqui. Geralmente a gente ta acostumado nos cursos e no kaggle, que ta tudo em um notebook só: treinamento e previsão. Nesse caso a gente ta pegando como se a gente tivesse parado na parte de treinamento e agora a gente pode usar isso pra fazer a previsão. Carregando isso aqui estamos carregando o objeto do modelo exatamente como estava na hora que salvamos. POr isso e importante saber as versões de bibliotecas que estamos usando pra informar pro app pra nao ter problemas de compatibilidades, vamos ver isso em breve. 
# Criamos propositalmente fora de todas as funções pra que eles possam ser acessados por qualquer função necessaria, apesar que a gente so vai usa-los em uma função e poderiam ser carregados na função especifica. Outra vantagem é que eles ja ficam na memoria, entao se for um modelo muito pesado de carregar, so precisamos carregar uma vez. 
mdl_rf = jb.load("random_forest_20200208.pkl.z")
mdl_lgbm = jb.load("lgbm_20200208.pkl.z")
title_vec = jb.load("title_vectorizer_20200208.pkl.z")



# clean_date, mesma limpeza que fizemos, so que agora precisamos mudar algumas coisas pq nao temos o pandas. Emtão pra facilitar bastante a nossa vida, criamos as funções recebendo o dicionario inteiro de dados, com as informações e so pegando aquilo que é necessario pra fazer essa função. 

# Aqui vamos usar a biblioteca de expressões regulares do python pra achar a mesma expressão regular que usamos com a função do pandas la na hora de limpar pra fazer o modelo, se não achar nada, ele retorna NaN. Se deu NaN e nao achou data, isso é um sinal que há problema com essa pagina, logo a gente nao deve fazer previsão pra essa pagina pois nao tem as info necessarias.

def clean_date(data):
    if re.search(r"(\d+) de ([a-z]+)\. de (\d+)", data['watch-time-text']) is None:
        return None
    
    # Aqui, quando rodamos raw_date_str_list, ele retorna os grupos de captura da expressão regular, no caso dia, mês e ano. 
    raw_date_str_list = list(re.search(r"(\d+) de ([a-z]+)\. de (\d+)", data['watch-time-text']).groups())
    #print(raw_date_str_list)
    # E aqui vamos ver que: devemos lembrar que no momento da modelagem deviamos adicionar um '0' na frente de numeros do dia que tivessem um digito, pra que o pandas entedesse que era uma data pro pandas formatar e trasnformar em um objeto data. Aqui estamos fazendo a mesma coisa, se o primeiro elemento que é o dia tiver tamanho 1, adiciona um 0 na frete.
    if len(raw_date_str_list[0]) == 1:
        raw_date_str_list[0] = "0"+raw_date_str_list[0]

    # Mesma coisa na hora de processar os meses, to pegando o elemento 1, que se refere aos meses: 0 é dia, 1 é mês e 2 é ano. E entao aplicamos o mapa meses, vai estar a abreviação de meses em portugues, e aplicamos o mapa para trocar para como o pandas espera o mês.
    raw_date_str_list[1] = mapa_meses[raw_date_str_list[1]]
    
    # Precisamos transformar tudo isso em uma string pra passar pra função to_datetime, e juntamos os elementos por espaço. E transformamos tudo em uma string.
    clean_date_str = " ".join(raw_date_str_list)

    # e ele retorna o o objeto datetime, para que possamos manipular.
    return pd.to_datetime(clean_date_str, format="%d %b %Y")



# Agora vamos limpar o campo de visualizações, novamente estamos usando a biblioteca de  expressão regular do python pra achar o numero que queremos nesse campo 'watch-view-count', se for NaN, é nesse caso queremos retornar que tem 0 visualização o video. 
def clean_views(data):
    raw_views_str = re.match(r"(\d+\.?\d*)", data['watch-view-count'])
    if raw_views_str is None:
        return 0
    # Aqui no raw_views_str, to pegando o group 1, que é o group de captura, se pegar o group 0, ele pega a expressão inteira, que da na mesma, mas em geral não da na mesma. E fazemos o replace do '.' por nada, pq o python precisa entender que esses numeros estão na casa de milhares, mas esse ponto seria como uma virgula.
    raw_views_str = raw_views_str.group(1).replace(".", "")
    #print(raw_views_str)

    # e então retorna os valores 'int' de visualizações.
    return int(raw_views_str)


# FUNÇÃO IMPORTANTE, novamente, mario fez o maximo possivel pra pegar o dicionario inteiro e definindo dentro da função o que vamos usar.
def compute_features(data):
    
    # Se não tem esse campo, significa que deu algum problema.
    if 'watch-view-count' not in data:
        return None
    
    # pegamos a data da publicação e fazemos o 'clean_date', processo mostrado na função acima. Se não achar esse campo ele retorna none, e vai pular esse exemplo, nao vamos fazer previsão pq nao temos informação necessaria. 
    publish_date = clean_date(data)
    if publish_date is None:
        return None

    # views vai ser o numero inteiro de visualizações que vamos retornar com a função clean views, seja ele 0 ou maior que 0.
    views = clean_views(data)
    
    # O titulo vai ser watch-title.
    title = data['watch-title']
    
    # mario gosta de criar features como dicionario, pq posso, mesmo aqui podemos acessa-las pelo nome, e fica mais facil de ordenar, nao cometer erros bobos, como inverter a ordem das features.
    features = dict()
    
    # mesma coisa que fizemos nos notebooks de modelos, a diferença é que vamos pegar o dia de hoje menos a data de publicação. Não podemos colocar a data fixa que colocamos na modelagem, mas precisamos de numero positivos pq o modelo desconhece numero negativo, se colocarmos a mesma data de lá, ele vai ter numero negativos, pq ele foi publicado depois da data fixa e o modelo nao saberá o que fazer com eles. Esse é uma das questões que em produção muda um pouco como computamos a feature. E temos que ver se o modelo sobrevive a isso, nesse caso vai pq nao estamos usando diretamente essa feature, mas como uma medida de popularidade na hora de fazer a feature de views por dia, onde deve-se dividir as views pela quantidade de dias que está publicado. Tanto que deleto o tempo desde a publicação desse dicionario. Então até aqui computamos duas features numericas, views e views por dia. Essa função é aplicada a cada video.
    features['tempo_desde_pub'] = (pd.Timestamp.today() - publish_date) / np.timedelta64(1, 'D')
    features['views'] = views
    features['views_por_dia'] = features['views'] / features['tempo_desde_pub']
    del features['tempo_desde_pub']

    # hora de transformar o titulo em vetor, pegar o title_vec que é o vetorizaror tf-idf e passar uma lista com essa string do titulo. Se passar só a string ele nao vai entender, entao precisamos passar pra função uma lista contendo o elemento que é o titulo, titulo no caso só a string do nome do video. 
    vectorized_title = title_vec.transform([title])

    # ele retorna pra gente uma matriz csr, é um tipo de matriz esparsa. 
    #E estamos transformando em csr matrix uma array do numpy que contém os dois elementos de features, essas precisam ser as duas primeiras pois era assim quando treinamos na modelagem.
    num_features = csr_matrix(np.array([features['views'], features['views_por_dia']]))
    # agora usamos aquela função do scipy pra juntar as features numericas com a matriz de contagem de palavras do titulo.
    feature_array = hstack([num_features, vectorized_title])

    # e retornamos essa feature_array, é uma array gigante de 1 x numero de colunas, mesma coisa que pegar uma linha da matriz que usamos pra treinar ou validar o modelo. Não tem segredo passar informações novas pro modelo. A parte mais chata é computar, processar, limpar todas as informações para colocar no formato de feature que precisamos. 
    return feature_array


# Essa função usamos la em run_backend, ela vai chamar o compute_features com o 'data', aquele dicionario gigante de informações, ele retorna a 'feature_array' que vimos acima. Se a feature_array, for NaN, ele vai retornar 0 : não tem previsão pra esse video.
def compute_prediction(data):
    feature_array = compute_features(data)

    if feature_array is None:
        return 0

    # retorna probabilidade do video ser bom ou ruim. E passamos feature_array, passamos uma matriz esparsa de 1 pelo numero de colunas, e ele retorna uma array bidimensional, então selecionamos a linha 0 e o elemento 1, que é a probabilidade de ser da classa positiva. Quando usamos funções que seguem a API do sckit-learn, ele vai retornar a probabilidade de ser classe 0 e a proba de ser da classe 1 , por isso que tem esse [0] e [1] no final. 
    p_rf = mdl_rf.predict_proba(feature_array)[0][1]
    p_lgbm = mdl_lgbm.predict_proba(feature_array)[0][1]

    # ensemble dos dois modelos, random forest e lgbm. 
    p = 0.5*p_rf + 0.5*p_lgbm
    
    # essa log_data serviria pra gente fazer monitoramento do modelo em produção, precisamos sempre monitorar pra ver se ele ta recebendo os valores corretos e tal. COmo isso é um protótipo, nao teremos essa parte de monitoramento.
    # Mas o que eu salvo nesse 'log_data' ? salvo os dados originais, feature_array e a previsão. IR PRA FUNÇÃO 'log_data' ABAIXO PRA VER.
    
    #log_data(data, feature_array, p)

    return p

def log_data(data, feature_array, p):
# vamos aumentar o dicionario 'data', vamos colocar um campo com a previsão e outro com a feature_array, para que possamos ver se por alguma incompatibilidade o meu modelo começar a computar as features erradas, apesar das informações  originais estarem corretas, vamos poder olhar essa 'feature_array' e ver um baita vetor onde vamos saber que ta acontecendo alguma coisa errada, conseguir detectar em que ponto que ele começou a prever errado. Armazendo como uma lista pra nao dar conflitos quando transforma pra json.

# e a previsão tbm, pra ver historicamente se o modelo esta tendo 'auc' e 'ap' que esperamos, se as previsões estão no intervalo que eu espero. MAS NÃO VAMOS USAR AQUI.

    #print(data)
    video_id = data.get('og:video:url', '')
    data['prediction'] = p
    data['feature_array'] = feature_array.todense().tolist()
    
    # aqui a ideia era que armazenar ou em um arquivo ou banco de dados, e que cada chave video_id teria os dados relacionados a ele, que coletamos sobre ele.  
    #print(video_id, json.dumps(data))







