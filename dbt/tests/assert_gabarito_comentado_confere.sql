-- O gabarito citado no comentário deve bater com o oficial. Divergências conhecidas (2022-1 Q3 e Q17-FR) são erros
-- do gabarito comentado; a prova confirma o oficial. Por isso o teste só avisa.
{{ config(severity='warn', warn_if='> 2') }}
select id_questao, resposta, gabarito_no_comentario
from {{ ref('fct_questao') }}
where gabarito_no_comentario is not null and gabarito_no_comentario <> resposta
