-- Um exame por linha, com a média de acertos publicada e os links oficiais.
select
    e.id_exame,
    e.ano,
    e.numero,
    e.tipo,
    e.nome,
    case when e.tipo = 'Único' then e.ano || ' · EU' else e.ano || ' · ' || e.numero || 'º EQ' end as rotulo,
    case when e.tipo = 'Único' then 'Exame Único' else e.numero || 'º Exame de Qualificação' end as etapa,
    'Vestibular ' || e.ano as rotulo_ano,
    right(cast(e.ano as varchar), 2) || '·' || case when e.tipo = 'Único' then 'EU' else cast(e.numero as varchar) end as rotulo_curto,
    e.data_aplicacao,
    e.url_prova,
    e.url_gabarito,
    e.url_gabarito_comentado,
    e.url_conteudo_programatico,
    e.documentos_fora_do_site_oficial,
    round(avg(q.percentual_acertos), 1) as media_acertos,
    count(q.percentual_acertos) as questoes_com_percentual,
    count(*) filter (where q.anulada) as anuladas
from dim_exame as e
left join fct_questao as q using (id_exame)
group by all
order by e.id_exame
