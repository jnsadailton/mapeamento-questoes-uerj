-- O programa completo, uma linha por subitem da hierarquia canônica (Área › Eixo › Item › Subitem), com quantas
-- questões caíram, desde quando o subitem está no edital e as outras redações com que ele aparece em editais e
-- gabaritos comentados (seeds/dicionario_conteudo).
with chaves as (
    select
        d.id_conteudo,
        regexp_replace(trim(d.subitem_texto), '[.;:,]+$', '') as texto,
        trim(regexp_replace(lower(strip_accents(d.subitem_texto)), '[^a-z0-9]+', ' ', 'g')) as chave,
        trim(regexp_replace(lower(strip_accents(c.subitem)), '[^a-z0-9]+', ' ', 'g')) as chave_canonica
    from dicionario_conteudo as d
    inner join dim_conteudo as c using (id_conteudo)
    where c.nivel = 'subitem'
),

-- uma redação por chave normalizada (a primeira em ordem alfabética), sem a forma canônica
outras as (
    select id_conteudo, string_agg(texto, ' · ' order by texto) as outras_redacoes, count(*) as qtd_outras
    from (
        select id_conteudo, chave, min(texto) as texto
        from chaves
        where chave <> chave_canonica and chave <> ''
        group by id_conteudo, chave
    )
    group by id_conteudo
),

edital as (
    select id_subitem, min(ano) as no_edital_desde, count(distinct id_exame) as exames_no_edital
    from bridge_programa_ano
    group by id_subitem
)

select
    s.id_area,
    s.area,
    s.id_eixo,
    s.eixo,
    s.id_item,
    s.item,
    s.disciplina,
    i.vigente as item_vigente,
    coalesce(ri.qtd_questoes, 0) as questoes_item,
    s.id_conteudo as id_subitem,
    s.subitem,
    s.vigente as subitem_vigente,
    coalesce(rs.qtd_questoes, 0) as questoes_subitem,
    coalesce(rs.qtd_exames, 0) as exames_subitem,
    e.no_edital_desde,
    coalesce(e.exames_no_edital, 0) as exames_no_edital,
    o.outras_redacoes,
    coalesce(o.qtd_outras, 0) as qtd_outras
from dim_conteudo as s
inner join dim_conteudo as i on i.id_conteudo = s.id_item and i.nivel = 'item'
left join mart_recorrencia as ri on ri.nivel = 'item' and ri.id_conteudo = s.id_item
left join mart_recorrencia as rs on rs.nivel = 'subitem' and rs.id_conteudo = s.id_conteudo
left join edital as e on e.id_subitem = s.id_conteudo
left join outras as o on o.id_conteudo = s.id_conteudo
where s.nivel = 'subitem'
order by s.id_conteudo
