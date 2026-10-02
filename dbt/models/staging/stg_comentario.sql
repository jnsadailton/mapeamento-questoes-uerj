-- O comentário sem número de questão (Redação de 2021-1) fica de fora: a Redação não está no escopo.
select
    {{ id_questao('exame', 'questao', 'idioma') }} as id_questao,
    exame as id_exame,
    questao as numero,
    idioma,
    pagina,
    questao_no_comentario,
    cabecalho,
    gabarito as gabarito_no_comentario,
    percentual_acertos,
    nivel,
    objetivo,
    texto
from {{ source('bronze', 'comentario') }}
where questao is not null
