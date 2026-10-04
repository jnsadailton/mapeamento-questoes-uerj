# Site (Evidence)

Site estático do Mapa das Questões UERJ, feito com [Evidence](https://legacy-docs.evidence.dev/) (versão open source,
travada em `package.json`). Lê os marts de `../data/warehouse/uerj.duckdb`, gerados pelo dbt.

```bash
npm ci
npm run sources   # extrai as tabelas de sources/uerj/*.sql para Parquet
npm run build     # gera o site estático em build/
npm run dev       # servidor local com recarga automática
```

- `pages/`: uma página por arquivo Markdown (`+layout.svelte` é o cabeçalho e o rodapé comuns).
- `sources/uerj/`: as consultas que levam os dados do warehouse para o navegador.
- `static/logo-uerj.svg`: marca oficial da UERJ (kit de marca publicado pela universidade), usada para identificar a
  fonte dos dados.
- Cores: `evidence.config.yaml`, documentadas e validadas em `../docs/paleta-de-cores.md`.
- O site é publicado em `/mapeamento-questoes-uerj` (GitHub Pages); por isso o `basePath` no `evidence.config.yaml`.
