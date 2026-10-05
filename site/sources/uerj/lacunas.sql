-- Subitens do edital vigente com o histórico de cobrança desde 2016.
select
    l.id_subitem,
    d.area,
    l.disciplina,
    l.eixo,
    l.item,
    l.subitem,
    l.qtd_questoes,
    l.qtd_exames,
    l.ultimo_ano,
    l.anos_sem_cair,
    l.qtd_exames_no_edital,
    l.primeiro_ano_no_edital,
    l.nunca_caiu
from mart_lacunas as l
inner join dim_conteudo as d on d.id_conteudo = l.id_subitem
order by l.id_subitem
