-- Toda prova tem 60 questões (números 1 a 60) e todo exame do escopo está presente.
select id_exame, count(distinct numero) as questoes, min(numero) as primeira, max(numero) as ultima
from {{ ref('fct_questao') }}
group by id_exame
having count(distinct numero) <> 60 or min(numero) <> 1 or max(numero) <> 60

union all

select 'faltam exames' as id_exame, count(*), null, null
from {{ ref('dim_exame') }}
having count(*) <> 21
