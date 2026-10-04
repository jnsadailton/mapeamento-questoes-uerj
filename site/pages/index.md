---
title: Mapa das Questões UERJ
description: O que caiu nas provas objetivas do Vestibular Estadual da UERJ de 2016 a 2027, por área, eixo, item e subitem do programa.
sidebar_position: 1
hide_breadcrumbs: true
---

<script>
  const coresArea = {
    'Linguagens': 'area-lin',
    'Matemática': 'area-mat',
    'Ciências da Natureza': 'area-cnt',
    'Ciências Humanas': 'area-chs'
  };
  const ordemAreas = ['Linguagens', 'Matemática', 'Ciências da Natureza', 'Ciências Humanas'];
</script>

<section class="hero">
  <img class="hero-logo" src="/logo-uerj.svg" alt="Marca da UERJ" width="92" height="100" />
  <div>
    <p class="hero-sobre">Vestibular Estadual UERJ · provas objetivas de 2016 a 2027</p>
    <p class="hero-titulo">O que mais cai na UERJ, conteúdo por conteúdo</p>
    <p class="hero-texto">
      As 1260 questões dos Exames de Qualificação e do Exame Único, ligadas ao eixo, ao item e ao subitem do programa
      em que o gabarito comentado oficial as classifica. Filtre por vestibular, exame e disciplina e veja o que pesa
      mais, o que voltou a cair e o que nunca caiu.
    </p>
    <p class="hero-autor">Criado por <strong>Adailton Nascimento</strong></p>
  </div>
</section>

<div class="cta">
  <a class="cta-principal" href="/painel">Explorar o que mais cai →</a>
  <a class="cta-secundario" href="/questoes">Buscar uma questão</a>
</div>

```sql kpis
select
    (select count(*) from uerj.exames) as exames,
    (select count(distinct id_exame || '-' || numero) from uerj.questoes) as questoes,
    (select count(*) from uerj.lacunas where not nunca_caiu) / (select count(*) from uerj.lacunas) as cobertura,
    (select avg(percentual_acertos) / 100 from uerj.questoes) as media_acertos
```

<Grid cols=4>
  <BigValue data={kpis} value=exames title="Exames analisados" />
  <BigValue data={kpis} value=questoes fmt="0" title="Questões classificadas" />
  <BigValue data={kpis} value=cobertura fmt=pct0 title="Do edital 2027 já cobrado" />
  <BigValue data={kpis} value=media_acertos fmt=pct0 title="Acertos em média" />
</Grid>

## Destaques

```sql mais_caem
select rotulo, area, qtd_questoes, regularidade
from uerj.recorrencia
where nivel = 'item'
order by qtd_questoes desc
limit 5
```

```sql em_alta
select rotulo, area, taxa_anterior, taxa_recente
from uerj.recorrencia
where nivel = 'item' and tendencia = 'em alta'
order by taxa_recente - taxa_anterior desc
limit 5
```

```sql sumidos
select rotulo, area, ultimo_exame, exames_desde_ultimo, intervalo_medio
from uerj.recorrencia
where nivel = 'item' and sumido_que_volta
order by indice_atraso desc
limit 5
```

<div class="cartoes">
  <div class="cartao">
    <p class="cartao-titulo">Os itens que mais caem</p>
    <p class="cartao-sub">Questões desde 2016</p>
    <ol>
      {#each mais_caem as l}
        <li><span>{l.rotulo}</span><b>{l.qtd_questoes}</b></li>
      {/each}
    </ol>
    <a href="/painel">Ver o ranking completo →</a>
  </div>
  <div class="cartao">
    <p class="cartao-titulo">Em alta</p>
    <p class="cartao-sub">Questões por exame: antes de 2025 → 2025 a 2027</p>
    <ol>
      {#each em_alta as l}
        <li><span>{l.rotulo}</span><b>{Number(l.taxa_anterior).toFixed(1).replace('.', ',')} → {Number(l.taxa_recente).toFixed(1).replace('.', ',')}</b></li>
      {/each}
    </ol>
    <a href="/tendencias">Ver tendências →</a>
  </div>
  <div class="cartao">
    <p class="cartao-titulo">Sumidos que costumam voltar</p>
    <p class="cartao-sub">Caem de tempos em tempos e estão há mais tempo que o normal sem cair</p>
    <ol>
      {#each sumidos as l}
        <li><span>{l.rotulo}</span><b>desde {l.ultimo_exame}</b></li>
      {/each}
    </ol>
    <a href="/tendencias">Ver a lista completa →</a>
  </div>
</div>

Os destaques descrevem o que já caiu; não são previsão da próxima prova.

## Quanto cada área pesa em cada exame

```sql por_area
select rotulo_exame, id_exame, area, qtd_questoes
from uerj.incidencia
where nivel = 'area'
order by id_exame
```

<BarChart
  data={por_area}
  x=rotulo_exame
  y=qtd_questoes
  series=area
  seriesOrder={ordemAreas}
  seriesColors={coresArea}
  type=stacked
  swapXY=true
  sort=false
  labels=true
  stackTotalLabel=false
  yMax=60
  xAxisTitle=" "
  yAxisTitle="Questões"
  chartAreaHeight=380
  emptySet=pass
/>

Nos Exames de Qualificação a divisão é estável: Linguagens ocupa cerca de um terço da prova (21 questões, contando o bloco
de língua estrangeira), seguida de Ciências Humanas, Ciências da Natureza e Matemática. As primeiras questões giram em
torno de um texto comum e são classificadas em áreas variadas. No Exame Único (2021 a 2023), organizado por disciplina,
Ciências da Natureza ganha espaço e Linguagens perde.

## Por onde começar

<div class="guia">
  <a href="/painel"><b>O que mais cai</b><span>Filtre vestibular, exame e disciplina e veja o ranking de eixos, itens e subitens, com os links das provas.</span></a>
  <a href="/tendencias"><b>Tendências</b><span>O que está em alta, o que caiu em quase toda prova e o que sumiu mas costuma voltar.</span></a>
  <a href="/historico"><b>Histórico por conteúdo</b><span>Exame a exame, em que prova cada item e subitem caiu desde 2016.</span></a>
  <a href="/dificuldade"><b>Dificuldade</b><span>Onde os candidatos mais erram e o que cai muito e tem poucos acertos.</span></a>
  <a href="/lacunas"><b>Lacunas</b><span>O que está no edital de 2027 e nunca caiu.</span></a>
  <a href="/questoes"><b>Questões</b><span>Todas as questões com filtros, classificação e link para o PDF oficial.</span></a>
</div>

<style>
  .hero { display: flex; gap: 1.5rem; align-items: center; padding: 1.5rem 1.5rem 1.25rem; margin: 0.5rem 0 1rem;
          border-radius: 12px; background: hsl(var(--twc-primary) / 0.07); border-left: 4px solid hsl(var(--twc-accent)); }
  .hero-logo { flex: none; background: #fff; border-radius: 10px; padding: 6px; }
  .hero-sobre { margin: 0; font-size: 0.8rem; letter-spacing: 0.04em; text-transform: uppercase;
                color: hsl(var(--twc-primary)); font-weight: 600; }
  .hero-titulo { margin: 0.25rem 0 0.5rem; font-size: 1.9rem; line-height: 1.15; font-weight: 700;
                 color: hsl(var(--twc-base-heading)); }
  .hero-texto { margin: 0 0 0.5rem; max-width: 46rem; }
  .hero-autor { margin: 0; font-size: 0.85rem; color: hsl(var(--twc-base-content-muted)); }
  .cta { display: flex; flex-wrap: wrap; gap: 0.75rem; margin: 0 0 1.5rem; }
  .cta a { padding: 0.6rem 1.1rem; border-radius: 8px; font-weight: 600; text-decoration: none; }
  .cta-principal { background: hsl(var(--twc-primary)); color: hsl(var(--twc-primary-content)) !important; }
  .cta-secundario { border: 1px solid hsl(var(--twc-primary) / 0.5); color: hsl(var(--twc-primary)) !important; }
  .cartoes { display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: 1rem; margin: 0.5rem 0; }
  .cartao { border: 1px solid hsl(var(--twc-base-content) / 0.15); border-radius: 10px; padding: 1rem 1.1rem;
            background: hsl(var(--twc-base-100)); }
  .cartao-titulo { margin: 0; font-weight: 700; color: hsl(var(--twc-base-heading)); }
  .cartao-sub { margin: 0.1rem 0 0.6rem; font-size: 0.8rem; color: hsl(var(--twc-base-content-muted)); }
  .cartao ol { margin: 0 0 0.75rem; padding: 0; list-style: none; }
  .cartao li { display: flex; justify-content: space-between; gap: 0.75rem; padding: 0.3rem 0; font-size: 0.9rem;
               border-bottom: 1px solid hsl(var(--twc-base-content) / 0.08); }
  .cartao li span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .cartao li b { flex: none; font-variant-numeric: tabular-nums; }
  .cartao a, .guia a { color: hsl(var(--twc-primary)); font-size: 0.875rem; font-weight: 600; text-decoration: none; }
  .guia { display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: 0.75rem; }
  .guia a { display: flex; flex-direction: column; gap: 0.25rem; padding: 0.9rem 1rem; border-radius: 10px;
            border: 1px solid hsl(var(--twc-base-content) / 0.15); }
  .guia a:hover, .cartao:hover { border-color: hsl(var(--twc-primary) / 0.6); }
  .guia span { font-weight: 400; color: hsl(var(--twc-base-content)); }
  @media (max-width: 640px) {
    .hero { flex-direction: column; align-items: flex-start; padding: 1rem; }
    .hero-titulo { font-size: 1.5rem; }
  }
</style>
