# Paleta de cores

Referência visual do site. Os valores abaixo são aplicados em `site/evidence.config.yaml` (bloco `theme`); qualquer
mudança de cor precisa ser feita nos dois lugares e validada de novo.

## Marca

As cores da marca vêm do kit oficial da UERJ (`Marca_UERJ.zip`, publicado em uerj.br). O logo usado no site,
`site/static/logo-uerj.svg`, é o SVG oficial em cores, só sem os metadados do Illustrator.

| Papel | Hex | Uso |
|---|---|---|
| Azul UERJ | `#0072CE` | cor principal: links, botões, filtros, barras de uma série só |
| Dourado UERJ | `#AD841F` | detalhe decorativo (fio do cabeçalho); contraste de 3,4:1, não usar em texto pequeno |
| Vermelho UERJ | `#F9423A` | só no logo; não é usado em dados, para não ser lido como "erro" ou "alerta" |

## Tipografia

Inspirada no caderno de prova da UERJ, que usa Minion nos números das questões e Avenir no texto: **Crimson Pro**
(serifa) nos títulos e nos números grandes, **Figtree** (sem serifa) no texto, nas tabelas e nos filtros. As duas são
livres e ficam no próprio site (pacotes `@fontsource-variable`). O estilo global está em `site/components/estilo.css`.

O menu lateral é uma lista numerada (números na serifa dos títulos), na ordem sugerida de uso; a página aberta
fica com fundo azul claro.

## Superfícies e texto

| Papel e tinta | Claro | Escuro |
|---|---|---|
| Fundo da página (`base-100`) | `#fbfbf9` | `#0d1b2a` |
| Título (`base-heading`) | `#231f20` | `#f4f6f9` |
| Texto (`base-content`) | `#3a3638` | `#dce3ec` |
| Texto secundário (`base-content-muted`) | `#6b6567` | `#9fb0c3` |
| Principal (`primary`) | `#0072CE` | `#4da3ff` |
| Destaque (`accent`) | `#AD841F` | `#d4a93a` |

## Áreas do conhecimento (paleta categórica)

Cada área tem sempre a mesma cor, em todos os gráficos, mesmo quando um filtro esconde as outras. A ordem é fixa.

| Área | Token | Claro | Escuro |
|---|---|---|---|
| Linguagens | `area-lin` | `#0072CE` | `#3987e5` |
| Matemática | `area-mat` | `#eb6834` | `#d95926` |
| Ciências da Natureza | `area-cnt` | `#1baf7a` | `#199e70` |
| Ciências Humanas | `area-chs` | `#eda100` | `#c98500` |

Validação (script de paleta categórica, critérios de daltonismo protan/deutan/tritan e de visão normal):

- claro, sobre `#fbfbf9`: todos os critérios passam; pior par adjacente ΔE 9,1 (protan). Verde e amarelo ficam abaixo
  de 3:1 de contraste com o fundo, por isso todo gráfico com essas cores leva rótulo direto ou tabela;
- escuro, sobre `#0d1b2a`: todos os critérios passam, inclusive contraste ≥ 3:1; pior par adjacente ΔE 8,4 (protan).

Gráficos de dispersão nunca misturam as quatro áreas: um gráfico pequeno por área (as áreas do filtro), porque as
quatro cores juntas não passam no critério de "todos os pares" exigido para pontos sobrepostos (laranja e amarelo:
ΔE 4,8 deutan). Dentro de cada gráfico, os pontos usam a paleta de eixos abaixo.

## Eixos dentro de uma área (dispersão da Dificuldade)

Nos gráficos de frequência × acertos, cada ponto é um item (ou subitem) e a cor diz o eixo. Uma área tem até 4 eixos, e
nenhum conjunto de quatro cores passa no critério de "todos os pares" quando os pontos se sobrepõem. Por isso cada eixo
tem **cor e formato** (círculo, quadrado, triângulo, losango, na ordem do programa), com legenda em cada gráfico.

| Posição do eixo na área | Token | Claro | Escuro | Formato |
|---|---|---|---|---|
| 1º | `eixo-1` | `#0072CE` | `#3987e5` | círculo |
| 2º | `eixo-2` | `#E0A800` | `#d4a017` | quadrado |
| 3º | `eixo-3` | `#C2410C` | `#c9531f` | triângulo |
| 4º | `eixo-4` | `#3FA9F5` | `#6cc0f7` | losango |

Validação com todos os pares: claro, sobre `#fbfbf9`, todos os critérios passam (pior par ΔE 16,5 protan; visão normal
16,1). Escuro, sobre `#0d1b2a`: separação para daltonismo (ΔE 14,6) e visão normal (16,6) passam; o amarelo e o azul
claro ficam um pouco acima da faixa de luminosidade, o que o formato do ponto compensa.

## Escala sequencial (mapas de calor)

Um só tom, do azul UERJ: claro `#d6e8f8` → `#00427a`; escuro `#0d2a47` → `#9cc8f0`. Célula vazia = nenhuma questão.

## Regras de uso

- Cor identifica a área, nunca a posição no ranking.
- Texto nunca usa a cor da série: valores e rótulos ficam nas cores de texto.
- Uma série só (ranking de um conteúdo, média por exame) usa o azul principal.
- Verde/vermelho não são usados para "bom/ruim" em dificuldade; a escala de acertos é sequencial.
