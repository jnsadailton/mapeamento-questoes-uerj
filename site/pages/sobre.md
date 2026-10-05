---
title: Sobre
description: De onde vêm os dados, como as questões são classificadas e quais são as limitações.
sidebar_position: 9
---

O **Mapa das Questões UERJ** foi criado por [**Adailton Nascimento**](https://www.linkedin.com/in/adailton-araujo-nascimento/), como projeto independente, público e gratuito. Não
tem ligação com a UERJ. Todos os dados vêm de documentos oficiais publicados pela universidade, e o código está aberto no
[GitHub](https://github.com/jnsadailton/mapeamento-questoes-uerj). A marca da UERJ aparece no site para identificar a
fonte dos dados; o arquivo é o oficial, do kit de marca publicado pela universidade.

## Escopo

As provas objetivas do Vestibular Estadual da UERJ, dos vestibulares 2016 a 2027: o 1º e o 2º Exame de Qualificação
de cada vestibular e o Exame Único de 2021, 2022 e 2023, ao todo 21 exames de 60 questões. Ficam de fora o Exame Discursivo, a Redação e os
simulados.

<AnoVestibular />

## Como os dados são produzidos

<pre class="diagrama">PDFs oficiais ──► Ingestão ──► Extração ──► Transformação ──► Este site
(UERJ, Wayback     (Python)     (PyMuPDF,    (dbt + DuckDB,      (Evidence,
 Machine)                        Parquet)     testes de dados)    estático)</pre>

<style>
  .diagrama { font-size: 0.8rem; line-height: 1.4; overflow-x: auto; padding: 0.75rem 1rem; border-radius: 6px;
              border: 1px solid rgba(127, 127, 127, 0.25); }
</style>

1. **Ingestão.** Para cada exame, quatro PDFs: prova, gabarito, conteúdo programático do edital e gabarito comentado.
   Cada arquivo é conferido para garantir que é idêntico ao original publicado pela UERJ. Se o site da UERJ estiver
   fora do ar, o arquivo vem de uma captura do Wayback Machine ou da cópia guardada no repositório.
2. **Extração.** O texto dos PDFs é lido com a posição na página, porque nos gabaritos comentados a ordem do texto vem
   embaralhada. Cada comentário é ligado ao rótulo "QUESTÃO NN" pela posição.
3. **Transformação.** Os editais mudam a redação dos conteúdos de um ano para outro. Para comparar os anos, todo texto
   de eixo, item e subitem passa por uma **hierarquia única** (Área › Eixo › Item › Subitem), com base no edital de
   2027, e um dicionário liga cada redação antiga ao conteúdo atual equivalente.
4. **Testes.** Cada atualização confere, entre outras coisas: 60 questões por exame, gabarito só de A a D ou anulada,
   as anuladas oficiais, toda questão não anulada classificada e nenhum texto sem ligação com a hierarquia.

## Como as questões são contadas

- A classificação de cada questão é a do **gabarito comentado oficial** da UERJ.
- Uma questão pode ter mais de uma classificação e conta para cada conteúdo citado.
- No bloco de língua estrangeira, cada idioma tem uma versão da questão. Na **incidência** (o que caiu), a unidade é o
  número da questão: um conteúdo citado nas três versões conta uma vez. Na **dificuldade**, cada versão tem o próprio
  percentual de acertos e conta separadamente.
- **Disciplinas.** Em Ciências da Natureza, cada item do programa é de Biologia, Física ou Química. Em Linguagens, o
  edital tem um programa só para Língua Portuguesa, Literatura e Língua Estrangeira: as questões em português são de
  Língua Portuguesa ou Literatura conforme o item, e as do bloco de língua estrangeira formam a disciplina Língua
  Estrangeira.
- Quando o comentário só informa o item, a questão conta para o item, mas não para nenhum subitem.
- As anuladas entram na incidência (o conteúdo foi cobrado) e ficam fora da dificuldade.

## Os indicadores

| Indicador | O que mede |
|:---|:---|
| **Questões** | Quantos números de questão tocaram o conteúdo. As versões de língua estrangeira do mesmo número contam uma vez. |
| **% das questões** | A fatia da seleção que o conteúdo ocupa. |
| **Regularidade** | Em que fração dos exames com o conteúdo no edital ele caiu. 100% = caiu em todos. |
| **Concentração** | Quantos conteúdos, do mais ao menos cobrado, somam metade das questões da seleção. |
| **Tendência** | Questões por exame nos 6 exames mais recentes (vestibulares 2025 a 2027) contra os anteriores. "Em alta": pelo menos 2 questões recentes e taxa 50% maior. "Em baixa": pelo menos 3 questões antes e taxa reduzida à metade. |
| **Intervalo normal** | O número médio de exames entre uma cobrança e a seguinte. |
| **Atraso** | Exames desde a última cobrança divididos pelo intervalo normal (só para o que caiu 3 vezes ou mais). |
| **Sumido que costuma voltar** | Do edital vigente, caiu 3 vezes ou mais e está com atraso de 1,5 ou mais (no mínimo 2 exames sem cair). |
| **Pontos perdidos** | Questões do conteúdo × taxa média de erro: quantas dessas questões um candidato típico errou. |
| **Diferencial** | Conteúdo que cai mais que a média e tem menos acertos que a média: saber é um diferencial, porque a maioria erra. |
| **Lacuna** | Subitem do edital mais recente (Vestibular 2027) em que nenhuma questão foi classificada desde o Vestibular 2016. *Antiga*: está no edital desde antes do Vestibular 2021; *recente*: entrou no de 2021 ou depois. As provas objetivas de 2027 já foram aplicadas; se o subitem continuar no próximo edital, pode cair. |

Todos descrevem o que já aconteceu. A banca não segue uma fila, então nenhum deles é previsão da próxima prova.

## O que o projeto completou

Alguns comentários oficiais vêm incompletos ou com campos trocados (o eixo no lugar do item, um item sem subitem). Nesses
casos o projeto completa a classificação a partir do edital do próprio exame e registra um **adendo** que aparece junto
da questão em todo o site. Uma questão do 2º Exame de 2024 (Q38) não tem comentário no PDF oficial e foi classificada
pelo projeto, com o nível de dificuldade estimado.

```sql adendos
select
    count(*) filter (where observacoes is not null) as questoes_com_adendo,
    count(*) as questoes
from uerj.questoes
```

Hoje, <Value data={adendos} column=questoes_com_adendo /> das <Value data={adendos} column=questoes fmt="0" /> versões de
questão têm adendo.

## Limitações

- **Percentual de acertos:** não há essa informação para 2021, 2024-2 e 2027-2, porque os gabaritos comentados desses
  exames não a trazem (os de 2021 e 2027-2 também não trazem o nível de dificuldade). Faltam também as anuladas e
  algumas questões de 2020-2 e 2022-1. A falta é da fonte oficial.
- **Gabarito comentado × gabarito oficial:** em 2022-1, as questões 3 e 17 (francês) têm gabarito diferente no
  comentário e no gabarito oficial. O site usa o oficial, que a prova confirma.
- **Lacunas:** um subitem que nunca caiu pode ter entrado no edital há pouco tempo. A página de lacunas mostra desde
  quando cada um está no edital.
- **Equivalência entre editais:** ligar uma redação antiga ao conteúdo atual exige julgamento em alguns casos. Cada
  decisão manual tem justificativa registrada no repositório.

## Fontes

```sql fontes
select
    case fonte_ultima_ingestao
        when 'uerj' then 'Site da UERJ'
        when 'wayback' then 'Wayback Machine'
        else 'Cópia do repositório'
    end as fonte,
    count(*) as documentos
from uerj.documentos
group by all
order by documentos desc
```

<DataTable data={fontes} emptySet=pass>
  <Column id=fonte title="De onde veio o PDF na última atualização" />
  <Column id=documentos title="Documentos" />
</DataTable>

```sql fora_do_site
select
    d.id_exame,
    case d.tipo
        when 'prova' then 'Prova'
        when 'gabarito' then 'Gabarito'
        when 'conteudo_programatico' then 'Conteúdo programático'
        else 'Gabarito comentado'
    end as documento,
    case d.fonte_ultima_ingestao when 'wayback' then 'Wayback Machine' else 'Cópia do repositório' end as fonte,
    coalesce(d.url_wayback, d.url_oficial) as link
from uerj.documentos as d
where d.fonte_ultima_ingestao <> 'uerj'
order by d.id_exame, d.tipo
```

Os documentos abaixo não estavam disponíveis no site da UERJ na última atualização (o endereço antigo saiu do ar ou o
arquivo foi removido) e vieram de uma cópia idêntica ao original:

<DataTable data={fora_do_site} rows=20 emptySet=pass emptyMessage="Todos os documentos vieram do site da UERJ.">
  <Column id=id_exame title="Exame" />
  <Column id=documento title="Documento" />
  <Column id=fonte title="Fonte" />
  <Column id=link title="Link" contentType=link linkLabel="abrir ↗" openInNewTab=true />
</DataTable>

- Provas e gabaritos: [vestibular.uerj.br](https://www.vestibular.uerj.br/)
- Gabaritos comentados: [revista.vestibular.uerj.br](https://www.revista.vestibular.uerj.br/questao/)
- Conteúdo programático: anexos dos editais de cada vestibular. Os de 2016 a 2018 ficam no servidor antigo da UERJ
  (sistema.vestibular.uerj.br), que ainda entrega os arquivos originais, mas com o certificado de segurança vencido; o
  navegador pode mostrar um aviso ao abrir esses links. O projeto confere se cada arquivo é idêntico ao original.
- O [Programa](/programa) lista todas as áreas, eixos, itens e subitens, com as redações dos editais antigos.
