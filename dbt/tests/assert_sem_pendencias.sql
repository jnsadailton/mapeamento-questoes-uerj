-- Nenhum texto de edital ou comentário pode ficar sem ligação com a hierarquia canônica.
select * from {{ ref('pendencias') }}
