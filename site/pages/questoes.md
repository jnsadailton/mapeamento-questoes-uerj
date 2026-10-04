---
title: Questões
description: Todas as questões objetivas desde 2016, com filtros, classificação e link para o PDF oficial.
sidebar_position: 7
---

Todas as questões objetivas de 2016 a 2027 com a classificação do gabarito comentado oficial. Use os filtros e a busca
(que procura em todas as colunas) e abra o comentário oficial pelo link.

```sql anos
select distinct ano, rotulo_ano from uerj.exames order by ano desc
```

```sql etapas
select etapa, min(numero) as ordem from uerj.exames group by etapa
```

```sql areas
select distinct area from uerj.conteudo order by area
```

<div class="filtros">

<Dropdown data={anos} name=anos value=ano label=rotulo_ano title="Vestibular" multiple=true selectAllByDefault=true order="ano desc" />

<Dropdown data={etapas} name=etapas value=etapa title="Exame" multiple=true selectAllByDefault=true order="ordem" />

<Dropdown data={areas} name=areas value=area title="Área" multiple=true selectAllByDefault=true />

<Dropdown name=versoes title="Versão" multiple=true selectAllByDefault=true>
  <DropdownOption value="Comum" valueLabel="Comum (fora do bloco de língua estrangeira)" />
  <DropdownOption value="Espanhol" />
  <DropdownOption value="Francês" />
  <DropdownOption value="Inglês" />
</Dropdown>

</div>

```sql lista
select
    id_questao,
    exame,
    numero,
    versao,
    area,
    disciplina,
    classificacao,
    eixos,
    resposta,
    percentual_acertos / 100 as acertos,
    nivel || case when nivel_estimado then ' (estimado)' else '' end as nivel,
    observacoes,
    url_prova,
    url_comentario
from uerj.questoes
where id_exame in (select id_exame from uerj.exames where ano in ${inputs.anos.value} and etapa in ${inputs.etapas.value})
    and area in ${inputs.areas.value}
    and versao in ${inputs.versoes.value}
order by id_exame desc, numero, idioma nulls first
```

<p class="contagem">{lista.length} versões de questão na seleção.</p>

<DataTable data={lista} rows=25 search=true downloadable=true emptySet=pass emptyMessage="Nenhuma questão nesta seleção.">
  <Column id=id_questao title="Questão" />
  <Column id=disciplina title="Disciplina" />
  <Column id=classificacao title="Item › Subitem" wrap=true />
  <Column id=resposta title="Gabarito" />
  <Column id=acertos title="Acertos" fmt=pct0 />
  <Column id=observacoes title="Adendo do projeto" wrap=true />
  <Column id=url_comentario title="Comentário" contentType=link linkLabel="PDF ↗" openInNewTab=true />
</DataTable>

- **Questão**: `AAAA-N-NN`, o ano do vestibular, o número do exame (o Exame Único usa 1) e o número da questão. No
  bloco de língua estrangeira, o sufixo indica o idioma (`-ES`, `-FR`, `-EN`).
- **Acertos**: percentual publicado pela UERJ. Fica vazio quando o gabarito comentado não o traz (2021, 2024-2,
  2027-2, anuladas e algumas questões de 2020-2 e 2022-1).
- **Adendo do projeto**: aparece quando o projeto completou, deduziu ou estimou parte da classificação. Todo o resto
  vem do PDF oficial.
- O link do comentário abre o gabarito comentado na página da questão.

<style>
  .filtros { display: flex; flex-wrap: wrap; gap: 0.25rem 0.75rem; align-items: flex-end; margin: 0.5rem 0 1rem; }
  .contagem { font-size: 0.85rem; color: hsl(var(--twc-base-content-muted)); }
</style>
