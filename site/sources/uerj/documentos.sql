-- Os PDFs de cada exame e a fonte de onde vieram na última atualização.
select
    id_exame,
    tipo,
    url_oficial,
    url_wayback,
    fonte_ultima_ingestao,
    obtido_em,
    sha256
from dim_documento
