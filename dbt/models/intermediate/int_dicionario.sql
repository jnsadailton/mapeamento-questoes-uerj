-- Dicionário de conteúdo com as chaves normalizadas (a mesma regra aplicada aos textos dos editais e comentários).
select
    {{ normalizar_texto('item_texto') }} as chave_item,
    {{ normalizar_texto('subitem_texto') }} as chave_subitem,
    id_conteudo,
    origem,
    metodo,
    justificativa
from {{ ref('dicionario_conteudo') }}
