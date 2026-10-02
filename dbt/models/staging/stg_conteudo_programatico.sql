select
    exame as id_exame,
    area as area_no_edital,
    eixo,
    item,
    subitem,
    ordem_item,
    ordem_subitem,
    pagina
from {{ source('bronze', 'conteudo_programatico') }}
