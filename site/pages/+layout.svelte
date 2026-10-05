<script>
	import '@fontsource-variable/crimson-pro';
	import '@fontsource-variable/figtree';
	import '../app.css';
	import '$lib/estilo.css';
	import { EvidenceDefaultLayout } from '@evidence-dev/core-components';
	import { addBasePath } from '@evidence-dev/sdk/utils/svelte';
	import { onMount } from 'svelte';
	import { onNavigate } from '$app/navigation';
	export let data;

	// Cada deploy pode trocar os arquivos de dados (o nome leva o hash do conteúdo) e apaga os antigos. Uma aba aberta
	// antes do deploy ainda tem o índice velho e falharia ao abrir outra página ("Failed to open file"). Ao navegar,
	// confere o índice; se mudou, carrega a página de novo em vez de navegar dentro da aba.
	const lerIndice = () =>
		fetch(addBasePath('/data/manifest.json'), { cache: 'no-cache' })
			.then((r) => (r.ok ? r.text() : null))
			.catch(() => null);
	let indice = null;
	onMount(async () => (indice = await lerIndice()));
	onNavigate(async (navegacao) => {
		if (!indice || !navegacao.to || navegacao.willUnload) return;
		const atual = await lerIndice();
		if (atual && atual !== indice) {
			window.location.assign(navegacao.to.url.href);
			return new Promise(() => {});
		}
	});
</script>

<EvidenceDefaultLayout
	{data}
	title="Mapa das Questões UERJ"
	homePageName="Início"
	maxWidth={1180}
	hideTOC={true}
	hideBreadcrumbs={true}
	neverShowQueries={true}
	builtWithEvidence={false}
	githubRepo="https://github.com/jnsadailton/mapeamento-questoes-uerj"
>
	<div slot="content">
		<slot />
		<footer class="rodape">
			<img class="rodape-logo" src={addBasePath('/logo-uerj.svg')} alt="Marca da UERJ" width="40" height="44" />
			<div>
				<p>
					Criado por <a href="https://www.linkedin.com/in/adailton-araujo-nascimento/" target="_blank" rel="noopener"><strong>Adailton Nascimento</strong></a>. Dados dos PDFs oficiais do Vestibular Estadual da
					UERJ (provas, gabaritos, gabaritos comentados e editais).
				</p>
				<p class="rodape-aviso">
					Projeto independente e gratuito, sem vínculo com a UERJ. A marca da universidade identifica a fonte
					dos dados. Código aberto no
					<a href="https://github.com/jnsadailton/mapeamento-questoes-uerj" target="_blank" rel="noopener">GitHub</a>;
					feito com Python, dbt, DuckDB e Evidence.
				</p>
			</div>
		</footer>
	</div>
</EvidenceDefaultLayout>

<style>
	.rodape {
		display: flex;
		gap: 1rem;
		align-items: flex-start;
		margin-top: 3rem;
		padding-top: 1.25rem;
		border-top: 2px solid hsl(var(--twc-accent));
		font-size: 0.85rem;
		color: hsl(var(--twc-base-content-muted));
	}
	.rodape p {
		margin: 0 0 0.35rem;
	}
	.rodape-aviso {
		font-size: 0.78rem;
	}
	.rodape-logo {
		flex: none;
		padding: 3px;
		border-radius: 6px;
		background: #ffffff;
	}
	.rodape a {
		color: hsl(var(--twc-primary));
	}
</style>
