-- Percentual entre 0 e 100, e vazio nos exames em que o gabarito comentado não o publica.
select id_questao, percentual_acertos
from {{ ref('fct_questao') }}
where percentual_acertos < 0
    or percentual_acertos > 100
    or (id_exame in ('{{ var("exames_sem_percentual") | join("', '") }}') and percentual_acertos is not null)
