-- Textos de eixo/item/subitem que não casaram com o dicionário (seeds/dicionario_conteudo.csv). Texto não pode
-- sumir: enquanto houver linha aqui, o teste `assert_sem_pendencias` falha. Para resolver, acrescente a chave ao
-- dicionário (`uv run python -m uerj.curadoria` sugere as ligações).
select distinct
    'classificacao' as origem,
    id_exame,
    id_questao,
    item as item_texto,
    parte_subitem as subitem_texto
from {{ ref('int_classificacao_ligada') }}
where id_conteudo is null

union all

select distinct
    'edital' as origem,
    id_exame,
    null as id_questao,
    item as item_texto,
    subitem as subitem_texto
from {{ ref('int_programa_ligado') }}
where id_conteudo is null
