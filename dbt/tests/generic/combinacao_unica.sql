{% test combinacao_unica(model, columns) %}
-- Falha se a combinação das colunas se repete.
select {{ columns | join(', ') }}, count(*) as repeticoes
from {{ model }}
group by {{ columns | join(', ') }}
having count(*) > 1
{% endtest %}
