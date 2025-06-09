# Visualização 1: Gráfico de Barras Agrupadas
# Comparando Aprovação, Reprovação e Abandono do Ensino Médio entre os estados.
if not df_plot.empty:
    fig1 = go.Figure()
    metricas = ['Aprovação (EM)', 'Reprovação (EM)', 'Abandono (EM)']
    nomes_legenda = ['Taxa de Aprovação', 'Taxa de Reprovação', 'Taxa de Abandono']

    for metrica, nome in zip(metricas, nomes_legenda):
        if metrica in df_plot.columns:
            fig1.add_trace(go.Bar(
                name=nome,
                x=df_plot['UF'],
                y=df_plot[metrica],
                text=df_plot[metrica].apply(lambda x: f'{x:.1f}%'), # Adiciona o valor no topo da barra
                textposition='auto'
            ))
        else:
            print(f"Aviso V1: Coluna '{metrica}' não encontrada para o gráfico de barras agrupadas.")


    fig1.update_layout(
        barmode='group',
        title_text='<b>Taxas de Rendimento do Ensino Médio por Estado (MG, SP, RJ) - 2023</b><br><i>Fonte: INEP (Dataset Kaggle)</i>',
        xaxis_title='Estado',
        yaxis_title='Taxa (%)',
        legend_title_text='Métricas do Ensino Médio',
        yaxis_ticksuffix="%" # Adiciona '%' ao eixo Y
    )
    print("\nExibindo Gráfico 1: Barras Agrupadas...")
    fig1.show()
else:
    print("Não há dados para gerar o Gráfico 1.")