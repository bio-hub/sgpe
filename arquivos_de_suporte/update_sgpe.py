#https://elasticsearch-saps.saude.gov.br/desc-esus-notifica-estado-pe/_search

#!pip install elasticsearch7==7.13.1
## Utilizar essa versão da biblioteca elasticsearch
##na versão 8 foi modificada a estrutra do arquivo é não funciona com o script no formato atual

import time
import pandas as pd
from elasticsearch7 import Elasticsearch
import elasticsearch7.helpers
import csv
import io
import datetime
import psycopg2

#consultar o ultimo registro no database
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="postgres",
    user="postgres",
    password="r>python" #coloque aqui sua senha
)

cur = conn.cursor()
cur.execute("SELECT MAX(CAST(TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS TIMESTAMP)) FROM sgpe")

ultimo_registro = cur.fetchall()

cur.close()
conn.close()


ultimo_registro_formatado = ultimo_registro[0][0].strftime("%Y-%m-%dT%H:%M:%S")


#variáveis atualizadas com as disponiveis na API do OpenDatasus em 24/01/2023
columns = ['id', 'dataNotificacao', 'sexo', 'racaCor', 'estado','estadoIBGE', 'municipio', 'municipioIBGE', 
           'estadoNotificacao', 'estadoNotificacaoIBGE', 'municipioNotificacao', 'municipioNotificacaoIBGE', 
           'sintomas', 'outrosSintomas', 'dataInicioSintomas', 'dataEncerramento', 'evolucaoCaso', 'classificacaoFinal', 
           'resultadoTeste', 'codigoTriagemPopulacaoEspecifica', 'resultadoTesteSorologicoIgG', 'outrasCondicoes', 
           'idade', 'loteSegundaReforcoDose', 'profissionalSaude', 'tipoTeste', 'resultadoTesteSorologicoIgM', 
           'resultadoTesteSorologicoTotais', 'qualAntiviral', 'codigoContemComunidadeTradicional', '@version', 
           'dataTesteSorologico', 'estrangeiro', 'idCollection', 'codigoDosesVacina', 'codigoLocalRealizacaoTestagem', 
           'laboratorioSegundaReforcoDose', 'dataSegundaDose', 'codigoEstrategiaCovid', 'dataSegundaReforcoDose',  
           'codigoRecebeuAntiviral', 'outroTriagemPopulacaoEspecifica', '@timestamp',  'outroBuscaAtivaAssintomatico', 
           'codigoBuscaAtivaAssintomatico', 'recebeuAntiviral', 'codigoRecebeuVacina', 'dataReforcoDose', 'tipoTesteSorologico', 
           'dataInicioTratamento', 'cbo', 'registroAtual', 'dataPrimeiraDose', 'condicoes', 'dataTeste', 'outroAntiviral', 
           'estadoTeste', 'codigoQualAntiviral', 'outroLocalRealizacaoTestagem']

#credenciais
user = 'seu username'
pwd = 'sua senha'
index = 'desc-esus-notifica-estado-pe'
protocol = 'https'
url = protocol + '://' + user + ':' + pwd +'@elasticsearch-saps.saude.gov.br' + '/'
es = Elasticsearch([url], send_get_body_as='POST', timeout=2000)

#query
update_cases={"query": {"bool": {"must": {"match_all": {}}, "filter": { "range": {"@timestamp": {"gte": "2019-01-01T00:00:00", "lte": "now"}}}}}}
update_cases["query"]["bool"]["must"]["match_all"] = {}
update_cases["query"]["bool"]["filter"]["range"]["@timestamp"]["gte"] = ultimo_registro_formatado

results = elasticsearch7.helpers.scan(es, query=update_cases, index=index)


#Recomendado a criação de um diretório chamado esus na pasta C:/ ou ajuste como preferir

with io.open('C:/Users/ronal/Downloads/esus/'+ index + '.csv', "w", encoding="utf-8", newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=columns, delimiter=';', extrasaction='ignore')
    writer.writeheader()
    i = 0
    printVal = 5000
    for document in results:
        writer.writerow(document['_source'])
        i += 1
