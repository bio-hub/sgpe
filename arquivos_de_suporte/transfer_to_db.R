#### carregamento das bibliotecas ####

#Executar scripts do python no R
library(reticulate)

#ETL dos dados
library(data.table)
library(DBI)
library(RPostgres)
library(tidyverse)

#criar rotinas no R
library(taskscheduleR)

#adicionar configuracao para nao converter os eixos dos valores para notação 
#científica
options(scipen = 999)

#### requisição das novas notificações ####

source_python(file = "C:/Users/ronal/OneDrive/portfoglio/data_sus/SG/arquivos_de_suporte/update_sgpe.py")

#### carregar o arquivo .csv com os novos registros ####

to_update = fread("C:/Users/ronal/Downloads/esus/desc-esus-notifica-estado-pe.csv")

#renomear os nomes das colunas
to_update = to_update %>%
  rename(timestamp = `@timestamp`) %>%
  rename(version = `@version`)
names(to_update) = tolower(names(to_update))

#### criar uma conexão do R com o postgreSQL #####

my_user = "postgres"
my_password = "r>python" #colocar sua senha aqui

con <- dbConnect(drv = RPostgres::Postgres(),
                 dbname="postgres",
                 host = "localhost",
                 port = 5432,
                 user = my_user,
                 password = my_password)

#### verificar se as novas entradas já estão presentes no database ####

ids = paste0(to_update$id, collapse = "','")

query = paste0("SELECT * FROM sgpe WHERE id IN ('", ids, "');")
result = dbGetQuery(con, query)

result = result %>%
  filter(registroatual == TRUE)

#eliminar das atualizações, as entradas já existentes

to_update = to_update %>%
  filter(registroatual == TRUE) %>%
  filter(!id %in% result$id)

#### transformação dos dados e carregamento no nosso database ####

#avaliar se precisa atualizar
if(nrow(to_update) > 0){
  
  #descobrir a última chave primária cadastrada no banco
  query = paste0("SELECT MAX(entry) FROM sgpe;")
  result = dbGetQuery(con, query)
  
  #adicionando a chave primária e novas colunas
  to_update = to_update %>%
    mutate(entry = seq(result$max+1, 
                       result$max+1+nrow(to_update)-1)) %>%
    relocate(entry, .before = "id")
  
  to_update = to_update %>%
    mutate(ano_notif = as.numeric(substr(datanotificacao, 1, 4))) %>%
    mutate(mes_notif = as.numeric(substr(datanotificacao, 6, 7)))
  
  #número de dias dos sintomas até a notificação
  x = interval(as.Date(to_update$datanotificacao),
               as.Date(to_update$datainiciosintomas))
  
  x= abs(x %/% days(1))
  
  to_update = to_update %>%
    mutate(dias_ate_notif = x)
  
  rm(x)
  
  #número de doses
  to_update = to_update %>%
    mutate(n_doses = gsub('"|\\[|\\]|\\|,',"", codigodosesvacina)) %>%
    mutate(n_doses = gsub("'| |,","", n_doses)) %>%
    mutate(n_doses = nchar(n_doses))
  
  #avaliar se o desfecho foi covid-19
  to_update = to_update %>%
    mutate(covid = case_when(!classificacaofinal %in% c("Síndrome Gripal Não Especificada",
                                                        "Descartado") ~ "covid",
                             classificacaofinal == "Síndrome Gripal Não Especificada" ~ "SG não especificada",
                             classificacaofinal == "Descartado" ~ "descartado")) %>%
    mutate(covid = if_else(is.na(classificacaofinal) == TRUE, NA, covid))
  
  #mudar valores vazios para NA
  to_update = to_update %>%
    mutate(sintomas = if_else(sintomas == "", NA, sintomas)) %>%
    mutate(condicoes = if_else(condicoes == "", NA, condicoes)) %>%
    mutate(racacor = if_else(racacor == "", NA, racacor)) %>%
    mutate(ano_notif = na_if(ano_notif, 2002)) %>% 
    mutate(evolucaocaso = if_else(evolucaocaso == "", NA, evolucaocaso)) %>%
    mutate(sexo = if_else(sexo == "", NA, sexo)) %>%
    mutate(municipionotificacao = if_else(municipionotificacao == "", NA, municipionotificacao)) %>%
    mutate(classificacaofinal = if_else(classificacaofinal == "", NA, classificacaofinal)) %>%
    mutate(datanotificacao = if_else(year(datanotificacao) == 2002, 
                                     NA ,
                                     datanotificacao))
  
  #carregar o dataframe para nossa tabela no PostgreSQL
  dbWriteTable(conn = con,
               name = "sgpe",   
               value = to_update,
               append = TRUE, 
               row.names = FALSE)
  
  #encerrar a conexão
  dbDisconnect(con)
  rm(con) 
} else {
  
  #encerrar a conexão
  dbDisconnect(con)
  rm(con) 
  
  print("não precisa atualizar!")
  
}