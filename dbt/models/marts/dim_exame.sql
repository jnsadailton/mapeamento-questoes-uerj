with exames as (
    select id_exame, min(data_aplicacao) as data_aplicacao
    from {{ ref('stg_gabarito') }}
    group by id_exame
),

fontes as (
    select
        id_exame,
        max(url_oficial) filter (where tipo = 'prova') as url_prova,
        max(url_oficial) filter (where tipo = 'gabarito') as url_gabarito,
        max(url_oficial) filter (where tipo = 'gabarito_comentado') as url_gabarito_comentado,
        max(url_oficial) filter (where tipo = 'conteudo_programatico') as url_conteudo_programatico,
        max(url_wayback) filter (where tipo = 'prova') as url_wayback_prova,
        count(*) filter (where fonte_ultima_ingestao <> 'uerj') as documentos_fora_do_site_oficial
    from {{ ref('stg_fontes') }}
    group by id_exame
)

select
    e.id_exame,
    cast(split_part(e.id_exame, '-', 1) as integer) as ano,
    cast(split_part(e.id_exame, '-', 2) as integer) as numero,
    case when split_part(e.id_exame, '-', 1) in ('2021', '2022', '2023') then 'Único' else 'Qualificação' end as tipo,
    case
        when split_part(e.id_exame, '-', 1) in ('2021', '2022', '2023')
            then 'Exame Único ' || split_part(e.id_exame, '-', 1)
        else split_part(e.id_exame, '-', 2) || 'º Exame de Qualificação ' || split_part(e.id_exame, '-', 1)
    end as nome,
    e.data_aplicacao,
    f.url_prova,
    f.url_gabarito,
    f.url_gabarito_comentado,
    f.url_conteudo_programatico,
    f.url_wayback_prova,
    f.documentos_fora_do_site_oficial
from exames as e
left join fontes as f using (id_exame)
