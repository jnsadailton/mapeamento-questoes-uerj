// Ajusta os componentes do Evidence 40 no node_modules: textos fixos em português (filtros, tabelas, botões dos
// gráficos e o menu dos três pontos), o menu lateral marcando a página atual, com os títulos das páginas como estão
// escritos, e a fonte dos gráficos igual à do site.
//
// O Evidence 40 não tem tradução: os textos estão escritos em inglês nos arquivos .svelte do pacote, que o Vite
// compila no build. E o menu lateral compara o endereço da página sem o basePath (/mapeamento-questoes-uerj), então
// nunca acha a página atual, e deixa "Início" sempre em destaque. Este script troca cada trecho e roda sozinho depois
// do `npm ci` (postinstall). Pode rodar de novo sem problema. Se um trecho não for encontrado (o pacote mudou de
// versão), o script avisa e falha, para a troca não sumir em silêncio.

import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const raiz = join(dirname(fileURLToPath(import.meta.url)), '..', 'node_modules', '@evidence-dev', 'core-components', 'dist');

// "Início" em destaque só quando é a página aberta, como os outros itens do menu
const INICIO =
	"class=\"sticky top-0 bg-base-100 shadow shadow-base-100 pb-1 mb-1 group inline-block transition-colors duration-100 {paginaAtual($page.url.pathname, '/') ? 'text-primary font-semibold' : 'text-base-content-muted hover:text-base-content'}\"";

const TROCAS = {
	'atoms/inputs/dropdown/Dropdown.svelte': [
		['{$selectedOptions.length} Selected', '{$selectedOptions.length} selecionados'],
		['<Command.Empty>No results found.</Command.Empty>', '<Command.Empty>Nada encontrado.</Command.Empty>'],
		['\t\t\t\t\t\t\t\t\t\tSelect all\n', '\t\t\t\t\t\t\t\t\t\tSelecionar todos\n'],
		['\t\t\t\t\t\t\t\t\tClear selection\n', '\t\t\t\t\t\t\t\t\tLimpar seleção\n']
	],
	'unsorted/viz/table/_DataTable.svelte': [
		['class:shownoresults={showNoResults}>No Results</div>', 'class:shownoresults={showNoResults}>Nada encontrado</div>'],
		['\t\t\t\t\t\tPage\n', '\t\t\t\t\t\tPágina\n'],
		[
			'{displayedPageLength.toLocaleString()} of {totalRows.toLocaleString()} records',
			"{displayedPageLength.toLocaleString('pt-BR')} de {totalRows.toLocaleString('pt-BR')} linhas"
		]
	],
	'unsorted/viz/table/EnterFullScreen.svelte': [['<span>Fullscreen</span>', '<span>Tela cheia</span>']],
	'unsorted/viz/core/SearchBar.svelte': [["export let placeholder = 'Search'", "export let placeholder = 'Buscar'"]],
	'unsorted/ui/DownloadData.svelte': [["export let text = 'Download';", "export let text = 'Baixar';"]],
	'organisms/layout/sidebar/Sidebar.svelte': [
		[
			"\timport { addBasePath } from '@evidence-dev/sdk/utils/svelte';\n",
			"\timport { addBasePath } from '@evidence-dev/sdk/utils/svelte';\n" +
				"\tconst semBarra = (c) => c.replace(/\\/+$/, '').toUpperCase();\n" +
				'\tconst paginaAtual = (caminho, href) => semBarra(caminho) === semBarra(addBasePath(href));\n'
		],
		[/\$page\.url\.pathname\.toUpperCase\(\) ===\s*(\w+)\.href\.toUpperCase\(\) \+ '\/'/g, 'paginaAtual($page.url.pathname, $1.href)'],
		["? 'text-primary'\n", "? 'text-primary font-semibold'\n"],
		[
			'class="sticky top-0 bg-base-100 shadow shadow-base-100 text-base-heading font-semibold pb-1 mb-1 group inline-block capitalize transition-colors duration-100"',
			INICIO
		],
		[
			'class="sticky top-0 bg-base-100 shadow shadow-base-100 font-semibold pb-1 mb-1 group inline-block capitalize hover:underline text-base-heading"',
			INICIO
		],
		// os títulos das páginas já vêm com as maiúsculas certas ("O que mais cai", não "O Que Mais Cai")
		[/ capitalize\b/g, '']
	],
	// gráficos com a mesma fonte do site (components/estilo.css)
	'../../component-utilities/src/echartsThemes.js': [
		["fontFamily: ['Inter', 'sans-serif']", "fontFamily: ['Figtree Variable', 'Segoe UI', 'sans-serif']"]
	],
	'unsorted/viz/core/ECharts.svelte': [
		['text="Save Image"', 'text="Salvar imagem"'],
		['text="Download Data"', 'text="Baixar dados"']
	],
	// menu dos três pontos: atalho de impressão Ctrl+P (⌘P só no Mac e no iPhone/iPad) e aparência em português
	'organisms/layout/header/KebabMenu.svelte': [
		[
			"\timport { dev } from '$app/environment';\n",
			"\timport { dev } from '$app/environment';\n" +
				"\timport { onMount } from 'svelte';\n" +
				"\tlet atalhoImprimir = 'Ctrl+P';\n" +
				"\tonMount(() => { if (/Mac|iPhone|iPad/i.test(navigator.platform || navigator.userAgent)) atalhoImprimir = '⌘P'; });\n"
		],
		['\t\t\t\tPrint PDF\n\t\t\t\t<DropdownMenu.Shortcut>⌘P</DropdownMenu.Shortcut>', '\t\t\t\tImprimir ou salvar PDF\n\t\t\t\t<DropdownMenu.Shortcut>{atalhoImprimir}</DropdownMenu.Shortcut>'],
		["{$showQueries ? 'Hide ' : 'Show '} Queries", "{$showQueries ? 'Esconder' : 'Mostrar'} consultas"],
		['\t\t\t\t\tAppearance\n', '\t\t\t\t\tAparência\n'],
		// um pouco mais largo, para o texto em português não encostar no atalho
		['<DropdownMenu.Content class="w-52 text-xs">', '<DropdownMenu.Content class="w-60 text-xs">'],
		["\t\t\t? 'System'\n", "\t\t\t? 'Sistema'\n"],
		["\t\t\t\t? 'Light'\n", "\t\t\t\t? 'Claro'\n"],
		["\t\t\t\t: 'Dark';", "\t\t\t\t: 'Escuro';"]
	]
};

let faltando = 0;
for (const [arquivo, trocas] of Object.entries(TROCAS)) {
	const caminho = join(raiz, arquivo);
	let texto = readFileSync(caminho, 'utf8').replaceAll('\r\n', '\n');
	for (const [de, para] of trocas) {
		const regex = de instanceof RegExp;
		const achou = regex ? texto.match(de) !== null : texto.includes(de);
		const feito = texto.includes(regex ? para.slice(0, para.indexOf('(') + 1) : para);
		// troca enquanto o original existir (a não ser que ele seja parte da própria troca, já feita)
		if (achou && !(feito && !regex && para.includes(de))) texto = texto.replaceAll(de, para);
		else if (!feito) {
			console.error(`traduzir-componentes: trecho não encontrado em ${arquivo}: ${JSON.stringify(String(de))}`);
			faltando += 1;
		}
	}
	writeFileSync(caminho, texto);
}
if (faltando) process.exit(1);
console.log('traduzir-componentes: componentes do Evidence ajustados');
