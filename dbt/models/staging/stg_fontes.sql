select
    f.exame as id_exame,
    f.tipo,
    f.arquivo,
    f.sha256,
    cast(f.tamanho as bigint) as tamanho_bytes,
    f.url_oficial,
    nullif(f.url_wayback, '') as url_wayback,
    cast(f.coletado_em as date) as coletado_em,
    p.fonte as fonte_ultima_ingestao,
    p.url as url_ultima_ingestao,
    cast(p.obtido_em as timestamp) as obtido_em,
    nullif(p.avisos, '') as avisos_ingestao
from {{ source('raw', 'fontes') }} as f
left join {{ source('raw', 'proveniencia') }} as p
    on p.exame = f.exame and p.tipo = f.tipo
