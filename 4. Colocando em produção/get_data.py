import requests as rq
import bs4 as bs4
import re
import time


# Esse simplesmente pegar e retorna o código fonte da pagina, response.text que a gente passa para o beatiful soup, o bs4.

def download_search_page(query, page):
    url = "https://www.youtube.com/results?search_query={query}&sp=CAI%253D&p={page}"
    urll = url.format(query=query, page=page)
    #print(urll)
    response = rq.get(urll)
    
    return response.text


# faz a mesma coisa, só que com a pagina do video, exatamente como lá no notebook de coleta.

def download_video_page(link):
    url = "https://www.youtube.com{link}"
    urll = url.format(link=link)
    response = rq.get(urll)
    
    link_name = re.search("v=(.*)", link).group(1)

    return response.text

# Mesma coisa dos primeiros notebooks de coletas, a gente vai pegar o beatifulsoup, pegar as tags. Se tiver duvida retornar la nos notebooks de coleta. Só que ao invés de guardar no arquivo parsed_videos.json, vamos pegar os dados e adicionar em video_list pq vamos retornar essa lista la pro run_backend. Essa video_list é resultado dessa função que pega os links dos videos.

def parse_search_page(page_html):
    parsed = bs4.BeautifulSoup(page_html)

    tags = parsed.findAll("a")

    video_list = []

    for e in tags:
        if e.has_attr("aria-describedby"):
            link = e['href']
            title = e['title']
            data = {"link": link, "title": title}
            video_list.append(data)
    return video_list


# Esse é o mais complicadinho, se tiver dúvida voltar la nos primeiros notebooks de coleta. Ao invés de salvar no arquivo a gente retorna o proprio dicionarios que criamos com todas as informações. Mandamos todos os dados mesmo, de forma bem bruta, mesmo que nao utilizemos todos, pq depois se for necessario novos testes e criação de features, nao precisarmos vir aqui de novo e mudar tudo. 

def parse_video_page(page_html):
    parsed = bs4.BeautifulSoup(page_html, 'html.parser')

    class_watch = parsed.find_all(attrs={"class":re.compile(r"watch")})
    id_watch = parsed.find_all(attrs={"id":re.compile(r"watch")})
    channel = parsed.find_all("a", attrs={"href":re.compile(r"channel")})
    meta = parsed.find_all("meta")

    data = dict()

    for e in class_watch:
        colname = "_".join(e['class'])
        if "clearfix" in colname:
            continue
        data[colname] = e.text.strip()

    for e in id_watch:
        colname = e['id']
        #if colname in output:
        #    print(colname)
        data[colname] = e.text.strip()

    for e in meta:
        colname = e.get('property')
        if colname is not None:
            data[colname] = e['content']

    for link_num, e in enumerate(channel):
        data["channel_link_{}".format(link_num)] = e['href']


    return data




# Não tem muito segredo colocar em produção essa parte de processamento de dados, e pegar o codigo que utilizamos pra puxar os codigos que usamos pra coletar/puxar os dados originalmente de algum banco de dados e transformar em funções que possamos usar pra rodar um exemplo de cada vez.