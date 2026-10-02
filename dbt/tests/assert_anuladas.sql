-- As anuladas são exatamente as da lista (var `anuladas` em dbt_project.yml), uma por exame.
with esperadas as (
    {% for exame, numero in var('anuladas').items() %}
    select '{{ exame }}' as id_exame, {{ numero }} as numero{% if not loop.last %} union all{% endif %}
    {% endfor %}
),

obtidas as (
    select distinct id_exame, numero from {{ ref('fct_questao') }} where anulada
)

select coalesce(e.id_exame, o.id_exame) as id_exame, e.numero as esperada, o.numero as obtida
from esperadas as e
full outer join obtidas as o using (id_exame, numero)
where e.numero is null or o.numero is null
