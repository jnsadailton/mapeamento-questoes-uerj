-- Partes das classificações ligadas à hierarquia canônica pelo dicionário. Uma parte pode apontar para mais de um
-- subitem (quando o comentário cita vários de uma vez); partes sem correspondência ficam com id_conteudo nulo e
-- aparecem no modelo `pendencias`.
select
    p.id_questao,
    p.id_exame,
    p.numero,
    p.idioma,
    p.ordem,
    p.eixo,
    p.item,
    p.subitem,
    p.parte_subitem,
    p.origem,
    p.eixo_atribuido,
    p.observacao,
    p.chave_item,
    p.chave_subitem,
    d.id_conteudo,
    d.metodo as metodo_ligacao
from {{ ref('int_classificacao_partes') }} as p
left join (select distinct chave_item, chave_subitem, id_conteudo, metodo from {{ ref('int_dicionario') }}) as d
    on d.chave_item = p.chave_item
    and d.chave_subitem = p.chave_subitem
