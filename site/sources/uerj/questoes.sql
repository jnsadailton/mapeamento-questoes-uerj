-- Uma linha por questão e idioma (no bloco de língua estrangeira, cada idioma é uma versão da questão), com a
-- classificação em texto e os links para a página da questão na prova e no gabarito comentado.
with conteudos as (
    select
        c.id_questao,
        string_agg(d.item || coalesce(' › ' || d.subitem, ''), ' | ' order by c.ordem, c.id_conteudo) as classificacao,
        string_agg(distinct d.eixo, ' | ' order by d.eixo) as eixos
    from fct_classificacao as c
    inner join dim_conteudo as d using (id_conteudo)
    group by c.id_questao
),

areas as (
    select distinct id_area, area from dim_conteudo
)

select
    q.id_questao,
    q.id_exame,
    e.ano,
    e.nome as exame,
    q.numero,
    q.idioma,
    case q.idioma when 'ES' then 'Espanhol' when 'FR' then 'Francês' when 'EN' then 'Inglês' else 'Comum' end as versao,
    a.area,
    q.disciplina,
    q.resposta,
    q.anulada,
    q.percentual_acertos,
    case q.nivel when 'facil' then 'fácil' when 'medio' then 'médio' when 'dificil' then 'difícil' end as nivel,
    q.nivel_estimado,
    q.objetivo,
    c.classificacao,
    c.eixos,
    q.observacoes,
    e.url_prova || '#page=' || q.pagina_prova as url_prova,
    e.url_gabarito_comentado || coalesce('#page=' || q.pagina_gabarito_comentado, '') as url_comentario
from fct_questao as q
inner join dim_exame as e using (id_exame)
left join areas as a using (id_area)
left join conteudos as c using (id_questao)
order by q.id_exame, q.numero, q.idioma nulls first
