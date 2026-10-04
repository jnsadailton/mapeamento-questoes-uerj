-- Percentual de acertos por item e subitem.
select
    m.nivel,
    m.id_conteudo,
    d.area,
    m.disciplina,
    d.eixo,
    d.item,
    d.subitem,
    m.rotulo,
    m.qtd_questoes,
    m.media_acertos,
    m.mediana_acertos,
    m.min_acertos,
    m.max_acertos
from mart_dificuldade as m
inner join dim_conteudo as d using (id_conteudo)
