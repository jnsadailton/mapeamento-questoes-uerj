-- Regularidade, recência, atraso e tendência de cada item e subitem (ver mart_recorrencia no dbt).
select * from mart_recorrencia
order by nivel, id_conteudo
