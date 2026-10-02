-- Classificações depois da curadoria: as extraídas dos gabaritos comentados, com o eixo completado por
-- seeds/eixos_atribuidos quando o comentário não o informa, e as de seeds/correcoes, que substituem todas as
-- classificações extraídas das questões que aparecem ali.
with corrigidas as (
    select distinct {{ id_questao('exame', 'questao', 'idioma') }} as id_questao
    from {{ ref('correcoes') }}
),

extraidas as (
    select
        c.id_questao,
        c.id_exame,
        c.numero,
        c.idioma,
        c.ordem,
        coalesce(c.eixo, e.eixo) as eixo,
        c.item,
        c.subitem,
        'gabarito_comentado' as origem,
        c.eixo is null and e.eixo is not null as eixo_atribuido,
        e.observacao
    from {{ ref('stg_classificacao') }} as c
    left join {{ ref('eixos_atribuidos') }} as e
        on e.exame = c.id_exame
        and e.questao = c.numero
        and coalesce(e.idioma, '') = coalesce(c.idioma, '')
        and e.item = c.item
    where c.id_questao not in (select id_questao from corrigidas)
),

das_correcoes as (
    select
        {{ id_questao('exame', 'questao', 'idioma') }} as id_questao,
        exame as id_exame,
        questao as numero,
        idioma,
        ordem,
        eixo,
        item,
        subitem,
        'correcao_' || tipo as origem,
        false as eixo_atribuido,
        observacao
    from {{ ref('correcoes') }}
)

select * from extraidas
union all
select * from das_correcoes
