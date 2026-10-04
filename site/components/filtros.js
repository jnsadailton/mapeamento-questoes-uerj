// Filtros das páginas (componente Filtro.svelte) e a cascata Área › Disciplina › Eixo › Item.
//
// A página carrega uma vez a hierarquia (uma linha por combinação de área, disciplina, eixo e item) e guarda a seleção
// de cada nível num objeto. As opções de cada nível são as que existem dentro do que está marcado nos níveis acima;
// quando um nível muda, os de baixo voltam a "todos" dentro das novas opções. A seleção vai para o `inputs_store` do
// Evidence no mesmo formato do Dropdown, então as consultas SQL continuam usando ${inputs.<nome>.value}.
//
// (O Dropdown do Evidence não serve para a cascata: ele guarda a seleção e as opções pelo nome e as restaura quando é
// recriado, e chegou a oferecer disciplinas de outra área.)

const literal = (v) => (typeof v === 'number' ? String(v) : `'${String(v).replaceAll("'", "''")}'`);

/** Linhas de um resultado de consulta do Evidence (vazio enquanto carrega). */
export const linhasDe = (q) => (q && q.length ? Array.from(q) : []);

/** Opções únicas [{ valor, rotulo }] de uma coluna, ordenadas por `ordenar` (padrão: pelo valor). */
export function unicas(linhas, valor, rotulo = valor, ordenar = (a, b) => String(a.valor).localeCompare(String(b.valor), 'pt')) {
	const vistos = new Map();
	for (const r of linhas) if (r[valor] != null && !vistos.has(r[valor])) vistos.set(r[valor], r[rotulo]);
	return [...vistos].map(([v, r]) => ({ valor: v, rotulo: String(r) })).sort(ordenar);
}

/** Ordena pela posição numa lista fixa (ex.: as quatro áreas na ordem do programa). */
export const naOrdem = (lista) => (a, b) => lista.indexOf(a.valor) - lista.indexOf(b.valor);

export const AREAS = ['Linguagens', 'Matemática', 'Ciências da Natureza', 'Ciências Humanas'];

/** Valor de input do Evidence para uma lista de valores (lista vazia não casa com nada). */
export function paraInput(valores, opcoes = []) {
	if (!valores || !valores.length) return { value: '(select null where 0)', label: '', rawValues: [] };
	const rotulos = new Map(opcoes.map((o) => [o.valor, o.rotulo]));
	const raw = valores.map((v) => ({ value: v, label: rotulos.get(v) ?? String(v), selected: true }));
	return { value: `(${valores.map(literal).join(',')})`, label: raw.map((r) => r.label).join(', '), rawValues: raw };
}

/**
 * Grava a seleção no `inputs_store` logo depois do ciclo de atualização atual. Gravar dentro de um `$:` não basta: as
 * consultas da página são declarações reativas que o Svelte já rodou nesse ciclo e não rodariam de novo.
 */
export function gravarInputs(store, valores) {
	queueMicrotask(() => store.update((v) => ({ ...v, ...valores })));
}

/**
 * Cascata de filtros. `niveis`: [{ nome, valor, rotulo?, ordenar? }], de cima para baixo.
 * - opcoes(linhas, sel): { nome: [{ valor, rotulo }] } de cada nível, dado o que está marcado acima;
 * - escolher(linhas, sel, nome, valores): nova seleção, com os níveis abaixo de `nome` de volta a "todos";
 * - inicial(linhas): tudo marcado.
 */
export function criarCascata(niveis) {
	function opcoes(linhas, sel) {
		const resultado = {};
		let atuais = linhas;
		for (const n of niveis) {
			resultado[n.nome] = unicas(atuais, n.valor, n.rotulo ?? n.valor, n.ordenar);
			const marcados = new Set(sel[n.nome] ?? []);
			atuais = atuais.filter((r) => marcados.has(r[n.valor]));
		}
		return resultado;
	}
	function escolher(linhas, sel, nome, valores) {
		const novo = { ...sel, [nome]: valores };
		const i = niveis.findIndex((n) => n.nome === nome);
		for (const n of niveis.slice(i + 1)) novo[n.nome] = opcoes(linhas, novo)[n.nome].map((o) => o.valor);
		return novo;
	}
	const inicial = (linhas) => escolher(linhas, {}, niveis[0].nome, opcoes(linhas, {})[niveis[0].nome].map((o) => o.valor));
	return { opcoes, escolher, inicial };
}
