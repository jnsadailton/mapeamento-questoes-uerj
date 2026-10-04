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

## Superfícies e texto

| Papel | Claro | Escuro |
|---|---|---|
| Fundo da página (`base-100`) | `#fbfbf9` | `#0f141a` |
| Título (`base-heading`) | `#0f1b2d` | `#f3f6fa` |
| Texto (`base-content`) | `#2b3440` | `#d7dee8` |
| Texto secundário (`base-content-muted`) | `#5f6b7a` | `#9aa7b6` |
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
- escuro, sobre `#0f141a`: todos os critérios passam, inclusive contraste ≥ 3:1.

Gráficos de dispersão mostram uma área por vez (filtro), porque as quatro cores juntas não passam no critério de
"todos os pares" exigido para pontos sobrepostos.

## Escala sequencial (mapas de calor)

Um só tom, do azul UERJ: claro `#d6e8f8` → `#00427a`; escuro `#0d2a47` → `#9cc8f0`. Célula vazia = nenhuma questão.

## Regras de uso

- Cor identifica a área, nunca a posição no ranking.
- Texto nunca usa a cor da série: valores e rótulos ficam nas cores de texto.
- Uma série só (ranking de um conteúdo, média por exame) usa o azul principal.
- Verde/vermelho não são usados para "bom/ruim" em dificuldade; a escala de acertos é sequencial.
