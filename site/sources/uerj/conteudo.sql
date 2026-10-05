-- Hierarquia canônica (uma linha por item e por subitem) e em quantos exames cada uma consta do edital.
select
    d.*,
    count(distinct b.id_exame) as qtd_exames_no_edital
from dim_conteudo as d
left join bridge_programa_ano as b
    on b.id_subitem = d.id_conteudo
    or (d.nivel = 'item' and b.id_subitem like d.id_conteudo || '.%')
group by all
order by d.id_conteudo
