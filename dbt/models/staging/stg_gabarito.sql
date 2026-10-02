select
    {{ id_questao('exame', 'questao', 'idioma') }} as id_questao,
    exame as id_exame,
    questao as numero,
    idioma,
    resposta,
    resposta = 'ANULADA' as anulada,
    data_aplicacao
from {{ source('bronze', 'gabarito') }}
