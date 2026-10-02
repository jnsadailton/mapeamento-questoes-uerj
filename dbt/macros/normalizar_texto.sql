{#
  Chave de comparação de textos de eixo, item e subitem: minúsculas, sem acento, sem pontuação e com as palavras
  partidas por quebra de linha emendadas ("uniforme- mente" -> "uniformemente"). É a mesma regra da função `n` usada
  na curadoria em Python (src/uerj/curadoria), para que as chaves do dicionário casem.
#}
{% macro normalizar_texto(coluna) -%}
trim(regexp_replace(
    regexp_replace(lower(strip_accents(coalesce({{ coluna }}, ''))), '(\w)- (\w)', '\1\2', 'g'),
    '[^a-z0-9]+', ' ', 'g'))
{%- endmacro %}


{#- Identificador da questão: AAAA-N-NN, com sufixo do idioma no bloco de língua estrangeira (-ES, -FR, -EN). -#}
{% macro id_questao(exame, questao, idioma) -%}
{{ exame }} || '-' || lpad(cast({{ questao }} as varchar), 2, '0') || coalesce('-' || {{ idioma }}, '')
{%- endmacro %}
