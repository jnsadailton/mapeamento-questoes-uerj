---
title: Mapa das Questões UERJ
description: O que caiu nas provas objetivas do Vestibular Estadual da UERJ de 2016 a 2027, por área, eixo, item e subitem do programa.
sidebar_position: 1
hide_breadcrumbs: true
hide_title: true
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
  <img class="hero-logo" src="/logo-uerj.svg" alt="Marca da UERJ" width="64" height="70" />
  <p class="hero-sobre">Vestibular Estadual da UERJ, provas objetivas dos vestibulares 2016 a 2027</p>
  <h1 class="hero-titulo">O que mais cai na UERJ, conteúdo por conteúdo</h1>
  <p class="hero-texto">
    As 1260 questões dos Exames de Qualificação e do Exame Único, ligadas ao eixo, ao item e ao subitem do programa em
    que o gabarito comentado oficial as classifica. Filtre por vestibular, exame e disciplina e veja o que pesa mais, o
    que voltou a cair e o que nunca caiu.
  </p>
  <div class="cta">
    <a class="cta-principal" href="/painel">Ver o que mais cai</a>
    <a class="cta-secundario" href="/questoes">Buscar uma questão</a>
  </div>
  <p class="hero-autor">Criado por <a href="https://www.linkedin.com/in/adailton-araujo-nascimento/" target="_blank" rel="noopener"><strong>Adailton Nascimento</strong></a></p>
</section>

<AnoVestibular />

```sql kpis
select
    (select count(*) from uerj.exames) as exames,
    (select count(distinct id_exame || '-' || numero) from uerj.questoes) as questoes,
    (select count(*) from uerj.lacunas where not nunca_caiu) / (select count(*) from uerj.lacunas) as cobertura,
    (select avg(percentual_acertos) / 100 from uerj.questoes) as media_acertos
```

<Grid cols=4>
  <BigValue data={kpis} value=exames title="Exames analisados" valueClass="valor" />
  <BigValue data={kpis} value=questoes fmt="0" title="Questões classificadas" valueClass="valor" />
  <BigValue data={kpis} value=cobertura fmt=pct0 title="Do edital do Vestibular 2027 já cobrado" valueClass="valor" />
  <BigValue data={kpis} value=media_acertos fmt=pct0 title="Acertos em média" valueClass="valor" />
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
    <a href="/painel">Ver o ranking completo</a>
  </div>
  <div class="cartao">
    <p class="cartao-titulo">Em alta</p>
    <p class="cartao-sub">Questões por exame, antes do Vestibular 2025 e de 2025 a 2027</p>
    <ol>
      {#each em_alta as l}
        <li><span>{l.rotulo}</span><b>{Number(l.taxa_anterior).toFixed(1).replace('.', ',')} → {Number(l.taxa_recente).toFixed(1).replace('.', ',')}</b></li>
      {/each}
    </ol>
    <a href="/tendencias">Ver as tendências</a>
  </div>
  <div class="cartao">
    <p class="cartao-titulo">Sumidos que costumam voltar</p>
    <p class="cartao-sub">Caem de tempos em tempos e estão há mais tempo que o normal sem cair</p>
    <ol>
      {#each sumidos as l}
        <li><span>{l.rotulo}</span><b>desde {l.ultimo_exame}</b></li>
      {/each}
    </ol>
    <a href="/tendencias">Ver a lista completa</a>
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

<Hierarquia compacto=true />

<div class="guia">
  <a href="/programa"><b>Programa</b><span>O dicionário completo: todas as áreas, eixos, itens e subitens, com busca e o que já caiu de cada um.</span></a>
  <a href="/painel"><b>O que mais cai</b><span>Filtre vestibular, exame, área, disciplina, eixo e item e veja o ranking em cada nível, com as questões e os links das provas.</span></a>
  <a href="/tendencias"><b>Tendências</b><span>O que está em alta, o que caiu em quase toda prova e o que sumiu mas costuma voltar.</span></a>
  <a href="/historico"><b>Histórico por conteúdo</b><span>Exame a exame, em que prova cada item e subitem caiu desde o Vestibular 2016.</span></a>
  <a href="/dificuldade"><b>Dificuldade</b><span>Onde os candidatos mais erram e o que é um diferencial saber: o que cai bastante e a maioria erra.</span></a>
  <a href="/lacunas"><b>Lacunas</b><span>O que está no edital do Vestibular 2027 e nunca caiu.</span></a>
  <a href="/questoes"><b>Banco de questões</b><span>Todas as questões com filtros, classificação e links para a prova e o gabarito comentado.</span></a>
</div>

<style>
  .hero { position: relative; margin: 0.25rem 0 2rem; padding: 0.5rem 0 1.75rem 5.5rem;
          border-bottom: 2px solid hsl(var(--twc-accent)); }
  .hero-logo { position: absolute; left: 0; top: 0.6rem; background: #fff; border-radius: 8px; padding: 5px; }
  .hero-sobre { margin: 0; font-size: 0.95rem; font-weight: 600; color: hsl(var(--twc-primary)); }
  .hero-titulo { margin: 0.3rem 0 0.9rem; max-width: 18ch; font-family: var(--fonte-titulo); font-size: 3.4rem;
                 line-height: 1.02; font-weight: 600; color: hsl(var(--twc-base-heading)); }
  .hero-texto { margin: 0 0 1.25rem; max-width: 62ch; font-size: 1.05rem; line-height: 1.6; }
  .hero-autor { margin: 1.1rem 0 0; font-size: 0.85rem; color: hsl(var(--twc-base-content-muted)); }
  .hero-autor a { color: hsl(var(--twc-primary)); text-underline-offset: 0.18em; }
  .cta { display: flex; flex-wrap: wrap; gap: 0.6rem; }
  .cta a { padding: 0.6rem 1.1rem; border-radius: 6px; font-weight: 600; text-decoration: none; }
  .cta-principal { background: hsl(var(--twc-primary)); color: hsl(var(--twc-primary-content)) !important; }
  .cta-principal:hover { background: hsl(var(--twc-primary) / 0.88); }
  .cta-secundario { border: 1.5px solid hsl(var(--twc-primary)); color: hsl(var(--twc-primary)) !important; }
  .cta-secundario:hover { background: hsl(var(--twc-primary) / 0.07); }
  .cartoes { display: grid; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); gap: 1.5rem 2rem; margin: 0.75rem 0; }
  .cartao { border-top: 2px solid hsl(var(--twc-base-heading)); padding-top: 0.75rem; }
  .cartao-titulo { margin: 0; font-family: var(--fonte-titulo); font-size: 1.35rem; line-height: 1.15; font-weight: 600;
                   color: hsl(var(--twc-base-heading)); }
  .cartao-sub { margin: 0.1rem 0 0.6rem; font-size: 0.82rem; color: hsl(var(--twc-base-content-muted)); }
  .cartao ol { margin: 0 0 0.75rem; padding: 0; list-style: none; counter-reset: pos; }
  .cartao li { display: flex; align-items: baseline; gap: 0.6rem; padding: 0.35rem 0; font-size: 0.92rem;
               border-bottom: 1px solid hsl(var(--twc-base-content) / 0.1); counter-increment: pos; }
  .cartao li::before { content: counter(pos); flex: none; width: 1.1rem; font-family: var(--fonte-titulo);
                       font-size: 1.15rem; font-weight: 600; color: hsl(var(--twc-primary)); }
  .cartao li span { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .cartao li b { flex: none; font-weight: 600; font-variant-numeric: tabular-nums; }
  .cartao a { color: hsl(var(--twc-primary)); font-size: 0.875rem; font-weight: 600; text-underline-offset: 0.18em; }
  .guia { display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: 0 2rem; }
  .guia a { display: flex; flex-direction: column; gap: 0.2rem; padding: 0.8rem 0; text-decoration: none;
            border-bottom: 1px solid hsl(var(--twc-base-content) / 0.12); }
  .guia b { font-family: var(--fonte-titulo); font-size: 1.2rem; font-weight: 600; color: hsl(var(--twc-primary)); }
  .guia a:hover b { text-decoration: underline; text-underline-offset: 0.18em; }
  .guia span { font-size: 0.92rem; color: hsl(var(--twc-base-content)); }
  @media (max-width: 640px) {
    .hero { padding-left: 0; }
    .hero-logo { position: static; margin-bottom: 0.75rem; }
    .hero-titulo { font-size: 2.4rem; }
  }
</style>
