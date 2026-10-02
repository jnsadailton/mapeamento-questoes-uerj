-- Toda questão não anulada tem pelo menos uma classificação, e toda classificação chega ao subitem ou ao item.
select id_questao
from {{ ref('fct_questao') }}
where not anulada and qtd_classificacoes = 0
