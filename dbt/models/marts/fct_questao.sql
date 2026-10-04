-- Uma linha por questão e idioma (no bloco de língua estrangeira, cada idioma é uma questão).
-- Percentual e nível vêm do gabarito comentado, ou de seeds/correcoes quando a questão foi transcrita ou
-- classificada à mão. A área e a disciplina principais são as da primeira classificação.
with correcao as (
    select
        {{ id_questao('exame', 'questao', 'idioma') }} as id_questao,
        max(percentual_acertos) as percentual_acertos,
        max(nivel) as nivel,
        bool_or(tipo = 'classificacao_manual') as classificacao_manual
    from {{ ref('correcoes') }}
    group by all
),

principal as (
    select id_questao, id_area, disciplina, count(*) over (partition by id_questao) as qtd_classificacoes
    from {{ ref('fct_classificacao') }}
    qualify row_number() over (partition by id_questao order by ordem, id_conteudo) = 1
),

observacoes as (
    select id_questao, string_agg(distinct observacao, ' ') as observacoes
    from {{ ref('fct_classificacao') }}
    where observacao is not null
    group by id_questao
)

select
    g.id_questao,
    g.id_exame,
    g.numero,
    g.idioma,
    g.resposta,
    g.anulada,
    coalesce(cr.percentual_acertos, c.percentual_acertos) as percentual_acertos,
    coalesce(cr.nivel, c.nivel) as nivel,
    coalesce(cr.classificacao_manual, false) as nivel_estimado,
    c.objetivo,
    c.gabarito_no_comentario,
    c.pagina as pagina_gabarito_comentado,
    pr.pagina as pagina_prova,
    p.id_area,
    p.disciplina,
    coalesce(p.qtd_classificacoes, 0) as qtd_classificacoes,
    o.observacoes
from {{ ref('stg_gabarito') }} as g
left join {{ ref('stg_comentario') }} as c using (id_questao)
left join {{ ref('stg_prova') }} as pr using (id_questao)
left join correcao as cr using (id_questao)
left join principal as p using (id_questao)
left join observacoes as o using (id_questao)
