-- Recorrência de cada item e subitem ao longo dos 21 exames: quantas vezes caiu, com que regularidade, quando caiu
-- pela última vez, qual o intervalo típico entre uma cobrança e outra e se está em alta ou em baixa.
--
-- Os exames são numerados em ordem (seq 1 = 2016-1, seq 21 = 2027-2) e os intervalos são medidos em exames. As
-- taxas usam como denominador os exames em que o conteúdo estava no edital, para não penalizar o que entrou há pouco.
-- Janela recente: os 6 últimos exames (vestibulares 2025 a 2027).
with exames as (
    select id_exame, row_number() over (order by id_exame) as seq, count(*) over () as total
    from {{ ref('dim_exame') }}
),

recentes as (
    select min(seq) as inicio from exames where seq > total - 6
),

ocorrencias as (
    select i.nivel, i.id_conteudo, i.id_exame, e.seq, e.total, i.qtd_questoes
    from {{ ref('mart_incidencia') }} as i
    inner join exames as e using (id_exame)
    where i.nivel in ('item', 'subitem')
),

intervalos as (
    select *, seq - lag(seq) over (partition by nivel, id_conteudo order by seq) as intervalo
    from ocorrencias
),

cobranca as (
    select
        nivel,
        id_conteudo,
        sum(qtd_questoes) as qtd_questoes,
        count(*) as qtd_exames,
        min(seq) as primeiro_seq,
        max(seq) as ultimo_seq,
        max(total) as total,
        avg(intervalo) as intervalo_medio,
        max(intervalo) as maior_intervalo,
        sum(qtd_questoes) filter (where seq >= (select inicio from recentes)) as qtd_recente,
        sum(qtd_questoes) filter (where seq < (select inicio from recentes)) as qtd_anterior
    from intervalos
    group by nivel, id_conteudo
),

-- Exames em que cada conteúdo estava no edital (o item conta quando qualquer subitem dele estava).
no_edital as (
    select 'subitem' as nivel, b.id_subitem as id_conteudo, e.seq
    from {{ ref('bridge_programa_ano') }} as b
    inner join exames as e using (id_exame)
    union
    select 'item', split_part(b.id_subitem, '.', 1) || '.' || split_part(b.id_subitem, '.', 2) || '.'
        || split_part(b.id_subitem, '.', 3), e.seq
    from {{ ref('bridge_programa_ano') }} as b
    inner join exames as e using (id_exame)
),

oportunidades as (
    select
        nivel,
        id_conteudo,
        count(*) as exames_no_edital,
        count(*) filter (where seq >= (select inicio from recentes)) as exames_no_edital_recente,
        count(*) filter (where seq < (select inicio from recentes)) as exames_no_edital_anterior
    from no_edital
    group by nivel, id_conteudo
),

base as (
    select
        c.*,
        coalesce(o.exames_no_edital, 0) as exames_no_edital,
        coalesce(o.exames_no_edital_recente, 0) as exames_no_edital_recente,
        coalesce(o.exames_no_edital_anterior, 0) as exames_no_edital_anterior,
        c.total - c.ultimo_seq as exames_desde_ultimo,
        coalesce(c.qtd_recente, 0) / nullif(o.exames_no_edital_recente, 0) as taxa_recente,
        coalesce(c.qtd_anterior, 0) / nullif(o.exames_no_edital_anterior, 0) as taxa_anterior
    from cobranca as c
    left join oportunidades as o using (nivel, id_conteudo)
)

select
    b.nivel,
    b.id_conteudo,
    d.id_area,
    d.area,
    d.disciplina,
    d.eixo,
    d.item,
    d.subitem,
    coalesce(d.subitem, d.item) as rotulo,
    d.vigente,
    b.qtd_questoes,
    b.qtd_exames,
    b.exames_no_edital,
    -- regularidade: em que fração dos exames com o conteúdo no edital ele caiu
    round(b.qtd_exames / nullif(greatest(b.exames_no_edital, b.qtd_exames), 0), 4) as regularidade,
    pe.id_exame as primeiro_exame,
    ue.id_exame as ultimo_exame,
    b.exames_desde_ultimo,
    round(b.intervalo_medio, 2) as intervalo_medio,
    b.maior_intervalo,
    -- atraso: exames desde a última cobrança divididos pelo intervalo típico (só com 3 cobranças ou mais)
    case when b.qtd_exames >= 3 then round(b.exames_desde_ultimo / b.intervalo_medio, 2) end as indice_atraso,
    coalesce(b.qtd_recente, 0) as qtd_recente,
    coalesce(b.qtd_anterior, 0) as qtd_anterior,
    round(b.taxa_recente, 3) as taxa_recente,
    round(b.taxa_anterior, 3) as taxa_anterior,
    case
        when b.exames_no_edital_anterior < 3 or b.exames_no_edital_recente < 3 then 'sem histórico'
        when coalesce(b.qtd_recente, 0) >= 2 and b.taxa_recente >= 1.5 * b.taxa_anterior then 'em alta'
        when coalesce(b.qtd_anterior, 0) >= 3 and b.taxa_recente <= 0.5 * b.taxa_anterior then 'em baixa'
        else 'estável'
    end as tendencia,
    -- "sumido que costuma voltar": caiu em 3 exames ou mais e está há bem mais tempo que o normal sem cair
    b.qtd_exames >= 3
        and b.exames_desde_ultimo >= greatest(2, ceil(1.5 * b.intervalo_medio))
        and d.vigente as sumido_que_volta
from base as b
inner join {{ ref('dim_conteudo') }} as d using (id_conteudo)
inner join exames as pe on pe.seq = b.primeiro_seq
inner join exames as ue on ue.seq = b.ultimo_seq
