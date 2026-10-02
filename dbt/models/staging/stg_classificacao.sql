select
    {{ id_questao('exame', 'questao', 'idioma') }} as id_questao,
    exame as id_exame,
    questao as numero,
    idioma,
    ordem,
    eixo,
    item,
    subitem
from {{ source('bronze', 'classificacao') }}
where questao is not null
