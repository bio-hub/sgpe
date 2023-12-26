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
update_cases={"query": {"bool": {"must": {"match_all": {}}, "filter": { "range": {"dataInicioSintomas": {"gte": "2019-01-01T00:00:00", "lte": "now"}}}}}}

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