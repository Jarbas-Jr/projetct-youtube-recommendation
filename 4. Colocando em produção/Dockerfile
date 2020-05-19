# Esse dockerfile vai ser o arquivo de configurações, as instruções que vamos dar para o contêiner.
# Esse FROM, é um ambiente pré-configurado.
# COPY esta simplesmente copiando os arquivos que temos pra uma pasta app, e ai ele vai tratar essa pasta app como a pasta onde ele deve rodar os comandos, entao os arquivos python vao parar dentro dessa pasta app, dentro do contêiner, dentro desse ambiente pré-configurado com todas as bibliotecas que precisamos. 

# Agora o grande problema vai do WORKDIR pra baixo, pq podemos rodar alguns comandos que vai instala algumas bibliotecas que precisamos. Então roda um 'apt-get update' pra ele atualizar os pacotes no linux. E vai instalar alguns pacotes que a gente precisa pra rodar o lighBGM, se nao vai dar erro, e isso mario achou olhando o docker do proprio LGBM, olhou no repositório do próprio LGBM e copiou os comandos necessarios de lá(https://github.com/microsoft/LightGBM/blob/master/docker/dockerfile-python).

# Depois vamos rodar 'pip install -r requirements.txt', pip é o gerenciador de pacotes do python. E quando passamos '-r' e um arquivo 'requitements' ele vai tentar instalar a lista de bibliotecas nesse arquivo(ABRIR O ARQUIVO AQUI NA PASTA) com suas respectivas versões. Deve-se colocar a versão pq ele pode instalar a versão mais nova e ai ele pode quebrar algum código nosso. Mas como encontramos a versão da biblioteca que estamos usando pra treinar o modelo e etc ?  Devemos abrir o terminal e colocar (pip freeze | grep 'nome da bib') e ele nos da a versão, dai é só copiar e jogar no requirements.txt.

# Em 'CMD python ./app.py' que está comentado, esse é comando que se quisermos rodar com o servidor do flask, podemos rodar esse arquivo, mas nao e recomendavel usar em produção. Entao aqui ja colocamos direto com um servidor mais robusto com um servidor recomendado com o próprio heroku. Mario descobriu esses comandos indo no github do heroku e na documentação e eles trazem esse exemplo, e mario abriu o dockerfile do exemplo que eles tem, o exemplo minimo de um contêiner docker que pode ser feito o deploy no heroku(https://github.com/heroku/alpinehelloworld/blob/master/Dockerfile). Mario foi ver quais o comandos, e eles estão usando 'G unicorn', servidor robusto pra se usar em produção. 

# LEMBRANDO: quando estivermos lidando com coisas em produção, bom perguntar pra quem entenda melhor parte de servidor, infraestrutura, devops, engenharia, pra ter certeza que estamos fazer do jeito seguro, que nao nos traga problemas depois e o foco aqui é na modelagem e não da engenharia. Então estamos fazendo uma solução basica pra colocar em produção e em boa parte do tempo nao vamos fazer uma aplicação que será exposta diretamente a um usuario na internet, pelo menos nao dessa maneira que tu ja entra e ja roda o flask ali. Geralmente vamos fazer API's internas que uma outra aplicação vai acabar fazendo a requisição, entao acaba sendo mais seguro. Mas definitivamente isso aqui acaba sendo mais de Engenharia de Machine Learning do que da ciencia de dados e da modelagem.

# Segundo a documentação do heroku, precisamos passar aqui 'CMD gunicorn --bind 0.0.0.0:$PORT wsgi'. e o cifrão PORT e pra colocar a porta que ele vai rodar.

# Se quisermos rodar localmente, descomentamos o comando '#CMD gunicorn --bind 0.0.0.0:80 wsgi ', e ai rodamos essa imagem do docker em um ambiente local(localhoost no linux). 

FROM python:3.7-slim
COPY . /app
WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        cmake \
        build-essential \
        gcc \
        g++ 
RUN pip install -r requirements.txt
RUN python db_starter.py
#CMD python ./app.py

# Run the image as a non-root user
#RUN adduser -D myuser
#USER myuser

# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku			
CMD gunicorn --bind 0.0.0.0:$PORT wsgi 
#CMD gunicorn --bind 0.0.0.0:80 wsgi 


#https://github.com/microsoft/LightGBM/blob/master/docker/dockerfile-python
#https://github.com/heroku/alpinehelloworld
#https://devcenter.heroku.com/articles/container-registry-and-runtime

#Creating app... done, ⬢ sheltered-reef-65520
#https://sheltered-reef-65520.herokuapp.com/ | https://git.heroku.com/sheltered-reef-65520.git