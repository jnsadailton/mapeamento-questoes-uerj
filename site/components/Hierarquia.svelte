<script>
	// Explica os quatro níveis do programa com um exemplo real. `compacto` mostra só a trilha.
	export let compacto = false;
	const niveis = [
		{ nome: 'Área', exemplo: 'Matemática', nota: '4 no total' },
		{ nome: 'Eixo', exemplo: 'Aritmética', nota: 'grandes temas da área' },
		{ nome: 'Item', exemplo: 'Proporcionalidade', nota: 'assunto dentro do eixo' },
		{ nome: 'Subitem', exemplo: 'porcentagem', nota: 'o tópico mais específico' }
	];
</script>

<div class="hierarquia" class:compacto>
	{#if !compacto}
		<p class="titulo">Como o programa da UERJ é organizado</p>
	{/if}
	<ol>
		{#each niveis as n, i}
			<li>
				<span class="nivel">{n.nome}</span>
				<span class="exemplo">{n.exemplo}</span>
				{#if !compacto}<span class="nota">{n.nota}</span>{/if}
			</li>
			{#if i < niveis.length - 1}<li class="seta" aria-hidden="true">›</li>{/if}
		{/each}
	</ol>
	{#if !compacto}
		<p class="texto">
			Cada nível fica dentro do anterior: o subitem "porcentagem" pertence ao item "Proporcionalidade", que pertence
			ao eixo "Aritmética", da área de Matemática. Escolher um item já inclui todos os subitens dele.
		</p>
	{/if}
</div>

<style>
	.hierarquia {
		margin: 0.75rem 0 1.25rem;
		padding: 0.9rem 1rem;
		border-radius: 8px;
		background: hsl(var(--twc-primary) / 0.06);
	}
	.compacto {
		padding: 0.5rem 0.75rem;
		margin: 0.25rem 0 0.75rem;
	}
	.titulo {
		margin: 0 0 0.6rem;
		font-family: var(--fonte-titulo);
		font-size: 1.2rem;
		font-weight: 600;
		color: hsl(var(--twc-base-heading));
	}
	ol {
		display: flex;
		flex-wrap: wrap;
		align-items: stretch;
		gap: 0.4rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	li:not(.seta) {
		display: flex;
		flex-direction: column;
		min-width: 8.5rem;
		padding: 0.45rem 0.7rem;
		border-radius: 8px;
		background: hsl(var(--twc-base-100));
		border: 1px solid hsl(var(--twc-primary) / 0.25);
	}
	.compacto li:not(.seta) {
		min-width: 0;
		padding: 0.25rem 0.55rem;
	}
	.seta {
		align-self: center;
		font-size: 1.3rem;
		color: hsl(var(--twc-primary));
	}
	.nivel {
		font-size: 0.75rem;
		font-weight: 600;
		color: hsl(var(--twc-primary));
	}
	.exemplo {
		font-weight: 600;
		color: hsl(var(--twc-base-heading));
	}
	.nota {
		font-size: 0.75rem;
		color: hsl(var(--twc-base-content-muted));
	}
	.texto {
		margin: 0.6rem 0 0;
		font-size: 0.9rem;
	}
</style>
