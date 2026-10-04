select
    {{ id_questao('exame', 'questao', 'idioma') }} as id_questao,
    exame as id_exame,
    questao as numero,
    idioma,
    pagina
from {{ source('bronze', 'prova') }}
