<script>
	// Filtro de seleção múltipla. As opções e a seleção vêm da página, que monta a cascata (Área › Disciplina › Eixo ›
	// Item) a partir da hierarquia: este componente só mostra e avisa a mudança com o evento `change` (detail = valores
	// selecionados, na ordem das opções).
	import { createEventDispatcher, tick } from 'svelte';

	export let titulo;
	export let opcoes = []; // [{ valor, rotulo }]
	export let selecionados = [];

	const avisar = createEventDispatcher();
	const id = 'filtro-' + Math.random().toString(36).slice(2, 9);
	let aberto = false;
	let busca = '';
	let raiz;
	let painel;
	let deslocamento = 0;

	// No celular, um filtro perto da borda direita abriria a lista para fora da tela: desloca a lista para dentro.
	async function abrir() {
		aberto = !aberto;
		deslocamento = 0;
		if (!aberto) return;
		await tick();
		const r = painel?.getBoundingClientRect();
		if (r) deslocamento = Math.min(0, window.innerWidth - 12 - r.right);
	}

	const normalizar = (t) => String(t ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

	$: marcados = new Set(selecionados);
	$: todos = opcoes.length > 0 && opcoes.every((o) => marcados.has(o.valor));
	$: rotulosMarcados = opcoes.filter((o) => marcados.has(o.valor)).map((o) => o.rotulo);
	$: resumo = !opcoes.length
		? 'sem opções'
		: todos
			? 'todos'
			: rotulosMarcados.length === 0
				? 'nenhum'
				: rotulosMarcados.length === 1
					? rotulosMarcados[0]
					: rotulosMarcados.length + ' selecionados';
	$: termo = normalizar(busca.trim());
	$: visiveis = termo ? opcoes.filter((o) => normalizar(o.rotulo).includes(termo)) : opcoes;

	function mudar(valores) {
		const conjunto = new Set(valores);
		avisar('change', opcoes.filter((o) => conjunto.has(o.valor)).map((o) => o.valor));
	}
	const alternar = (v) => mudar(marcados.has(v) ? selecionados.filter((x) => x !== v) : [...selecionados, v]);
	const so = (v) => mudar([v]);

	function fora(e) {
		if (aberto && raiz && !raiz.contains(e.target)) aberto = false;
	}
	function tecla(e) {
		if (aberto && e.key === 'Escape') aberto = false;
	}
</script>

<svelte:window on:click={fora} on:keydown={tecla} />

<div class="filtro" bind:this={raiz}>
	<button
		type="button"
		class="gatilho"
		class:parcial={!todos}
		aria-expanded={aberto}
		aria-controls={id}
		on:click={abrir}
	>
		<span class="titulo">{titulo}</span>
		<span class="resumo">{resumo}</span>
		<svg class="seta" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 4.5 6 7.5 9 4.5" /></svg>
	</button>
	{#if aberto}
		<div class="painel" id={id} role="group" aria-label={titulo} bind:this={painel} style={'left: ' + deslocamento + 'px'}>
			{#if opcoes.length > 1}
				<p class="dica">Marque quantos quiser, ou use <span class="exemplo-apenas">apenas</span> para ficar só com um.</p>
			{/if}
			{#if opcoes.length > 8}
				<input class="busca" type="search" placeholder="Buscar" bind:value={busca} aria-label={'Buscar em ' + titulo} />
			{/if}
			<ul>
				{#each visiveis as o (o.valor)}
					<li>
						<label>
							<input type="checkbox" checked={marcados.has(o.valor)} on:change={() => alternar(o.valor)} />
							<span>{o.rotulo}</span>
						</label>
						<button
							type="button"
							class="so"
							on:click={() => so(o.valor)}
							title={'Desmarcar os outros e ficar só com ' + o.rotulo}
							aria-label={'Selecionar apenas ' + o.rotulo}>apenas</button
						>
					</li>
				{:else}
					<li class="vazio">Nada encontrado.</li>
				{/each}
			</ul>
			<div class="acoes">
				<button type="button" on:click={() => mudar(opcoes.map((o) => o.valor))} disabled={todos}>Selecionar todos</button>
				<button type="button" on:click={() => mudar([])} disabled={!selecionados.length}>Limpar seleção</button>
			</div>
		</div>
	{/if}
</div>

<style>
	.filtro {
		position: relative;
		display: inline-block;
		margin: 0.25rem 0;
	}
	.gatilho {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		height: 2.1rem;
		max-width: 20rem;
		padding: 0 0.7rem;
		border-radius: 6px;
		font-size: 0.875rem;
		border: 1px solid hsl(var(--twc-base-content) / 0.25);
		background: hsl(var(--twc-base-100));
		color: hsl(var(--twc-base-content));
		cursor: pointer;
	}
	.gatilho:hover {
		border-color: hsl(var(--twc-primary));
	}
	.titulo {
		font-weight: 650;
		color: hsl(var(--twc-base-heading));
	}
	.resumo {
		min-width: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		color: hsl(var(--twc-base-content-muted));
	}
	.parcial .resumo {
		color: hsl(var(--twc-primary));
		font-weight: 600;
	}
	.seta {
		flex: none;
		width: 0.75rem;
		height: 0.75rem;
		fill: none;
		stroke: currentColor;
		stroke-width: 1.5;
	}
	.painel {
		position: absolute;
		z-index: 40;
		top: calc(100% + 4px);
		left: 0;
		width: max(16rem, 100%);
		max-width: min(24rem, 90vw);
		padding: 0.4rem;
		border-radius: 8px;
		border: 1px solid hsl(var(--twc-base-content) / 0.2);
		background: hsl(var(--twc-base-100));
		box-shadow: 0 8px 24px hsl(var(--twc-base-heading) / 0.12);
	}
	.busca {
		width: 100%;
		margin-bottom: 0.3rem;
		padding: 0.35rem 0.55rem;
		border-radius: 5px;
		font-size: 0.85rem;
		border: 1px solid hsl(var(--twc-base-content) / 0.25);
		background: hsl(var(--twc-base-100));
		color: hsl(var(--twc-base-content));
	}
	ul {
		max-height: 18rem;
		overflow-y: auto;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	li {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		border-radius: 5px;
	}
	li:hover {
		background: hsl(var(--twc-primary) / 0.07);
	}
	label {
		flex: 1;
		display: flex;
		align-items: flex-start;
		gap: 0.5rem;
		padding: 0.35rem 0.4rem;
		font-size: 0.875rem;
		line-height: 1.3;
		cursor: pointer;
	}
	label input {
		flex: none;
		margin-top: 0.15rem;
		accent-color: hsl(var(--twc-primary));
	}
	.dica {
		margin: 0.1rem 0.3rem 0.4rem;
		font-size: 0.78rem;
		line-height: 1.4;
		color: hsl(var(--twc-base-content-muted));
	}
	.so,
	.exemplo-apenas {
		flex: none;
		padding: 0.1rem 0.5rem;
		border: 1px solid hsl(var(--twc-primary) / 0.5);
		border-radius: 999px;
		font-size: 0.72rem;
		font-weight: 600;
		color: hsl(var(--twc-primary));
		background: hsl(var(--twc-base-100));
	}
	.exemplo-apenas {
		display: inline-block;
		padding: 0 0.4rem;
		line-height: 1.35;
	}
	.so {
		visibility: hidden;
		margin-right: 0.2rem;
	}
	.so:hover {
		background: hsl(var(--twc-primary));
		color: hsl(var(--twc-primary-content));
	}
	li:hover .so,
	.so:focus-visible {
		visibility: visible;
	}
	.vazio {
		padding: 0.4rem;
		font-size: 0.85rem;
		color: hsl(var(--twc-base-content-muted));
	}
	.acoes {
		display: flex;
		gap: 0.25rem;
		margin-top: 0.3rem;
		padding-top: 0.3rem;
		border-top: 1px solid hsl(var(--twc-base-content) / 0.12);
	}
	.acoes button {
		flex: 1;
		padding: 0.35rem;
		border-radius: 5px;
		font-size: 0.8rem;
		font-weight: 600;
		color: hsl(var(--twc-primary));
		background: transparent;
	}
	.acoes button:hover:not(:disabled) {
		background: hsl(var(--twc-primary) / 0.08);
	}
	.acoes button:disabled {
		color: hsl(var(--twc-base-content-muted) / 0.6);
		cursor: default;
	}
	@media (hover: none) {
		.so {
			visibility: visible;
		}
	}
</style>
