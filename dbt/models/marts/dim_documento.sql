-- Os 84 PDFs usados (4 por exame), com as URLs e a fonte de onde vieram na última ingestão. Alimenta a página "Sobre"
-- e o aviso do site quando um documento não veio do site oficial da UERJ.
select
    id_exame,
    tipo,
    arquivo,
    sha256,
    tamanho_bytes,
    url_oficial,
    url_wayback,
    coletado_em,
    fonte_ultima_ingestao,
    url_ultima_ingestao,
    obtido_em,
    avisos_ingestao
from {{ ref('stg_fontes') }}
