// Ajustes de gráficos para telas estreitas (celular).

/** Verdadeiro no navegador com tela estreita (abaixo do breakpoint `sm` do Tailwind). */
export const telaEstreita = () => typeof window !== 'undefined' && window.innerWidth < 640;

/**
 * echartsOptions para gráficos de barras deitadas (swapXY): no celular, o nome de cada barra é cortado com
 * reticências, senão os nomes ocupam quase toda a largura e as barras viram um traço. O nome inteiro aparece ao tocar.
 */
export const barrasDeitadas = () =>
	telaEstreita()
		? {
				// margens explícitas: sem elas, o começo dos nomes e o número da maior barra ficavam cortados
				grid: { containLabel: true, left: 4, right: 34 },
				yAxis: { axisLabel: { width: 112, overflow: 'truncate', ellipsis: '…' } }
			}
		: undefined;
