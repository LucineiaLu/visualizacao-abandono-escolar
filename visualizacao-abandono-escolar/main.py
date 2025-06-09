import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. Carregamento e Inspeção Inicial dos Dados ---
try:
    # O arquivo CSV usa ';' como delimitador e ',' como separador decimal
    df_completo = pd.read_csv('data/taxas-de-rendimento-escolar.csv', delimiter=';')
except FileNotFoundError:
    print("Erro: Arquivo 'taxas-de-rendimento-escolar.csv' não encontrado na pasta 'data'.")
    print("Verifique se o download e a descompactação foram feitos corretamente.")
    exit()

print("--- Amostra dos Dados Originais ---")
print(df_completo.head())
print("\n--- Informações Gerais do DataFrame ---")
df_completo.info()

# Colunas de taxas que precisam de conversão (de string com vírgula para float)
colunas_taxas = [
    'Taxa_Aprovacao_Ensino_Fundamental_Anos_Iniciais', 'Taxa_Aprovacao_Ensino_Fundamental_Anos_Finais', 'Taxa_Aprovacao_Ensino_Medio',
    'Taxa_Reprovacao_Ensino_Fundamental_Anos_Iniciais', 'Taxa_Reprovacao_Ensino_Fundamental_Anos_Finais', 'Taxa_Reprovacao_Ensino_Medio',
    'Taxa_Abandono_Ensino_Fundamental_Anos_Iniciais', 'Taxa_Abandono_Ensino_Fundamental_Anos_Finais', 'Taxa_Abandono_Ensino_Medio'
]

for col in colunas_taxas:
    if col in df_completo.columns:
        # Converte vírgula para ponto e depois para float. Erros são convertidos para NaN (não numérico)
        df_completo[col] = df_completo[col].str.replace(',', '.', regex=False).astype(float, errors='coerce')
    else:
        print(f"Aviso: Coluna de taxa esperada '{col}' não encontrada no CSV.")

# --- 2. Filtragem dos Dados ---
# Ano: 2023
# Estados: MG, SP, RJ (Região Sudeste)
# Nível de Agregação: Estadual (Rede='Total', Localizacao='Total')
# Para dados estaduais consolidados, geralmente 'Nome_Municipio' ou 'Codigo_Municipio' são nulos/NaN.

df_filtrado = df_completo[
    (df_completo['Ano'] == 2023) &
    (df_completo['UF'].isin(['MG', 'SP', 'RJ'])) &
    (df_completo['Rede'] == 'Total') &
    (df_completo['Localizacao'] == 'Total') &
    (df_completo['Nome_Municipio'].isna()) # Suposição comum para totais estaduais no INEP
].copy() # Usar .copy() para evitar SettingWithCopyWarning

# Verificação alternativa se o filtro acima não funcionar
if df_filtrado.empty:
    print("\nTentativa de filtro com 'Nome_Municipio' NaN não retornou dados. Tentando com 'Codigo_Municipio' NaN...")
    df_filtrado = df_completo[
        (df_completo['Ano'] == 2023) &
        (df_completo['UF'].isin(['MG', 'SP', 'RJ'])) &
        (df_completo['Rede'] == 'Total') &
        (df_completo['Localizacao'] == 'Total') &
        (df_completo['Codigo_Municipio'].isna()) # Alternativa para totais estaduais
    ].copy()

if df_filtrado.empty:
    print("\nErro Crítico: Não foi possível encontrar os dados estaduais consolidados para MG, SP, RJ em 2023 com os filtros aplicados.")
    print("Verifique a estrutura do arquivo CSV para entender como os totais por estado são representados.")
    print("Pode ser que 'Nome_Municipio' ou 'Codigo_Municipio' tenham um valor específico (ex: 'Não se aplica') em vez de NaN.")
    print("Ou pode ser necessário agregar os dados a partir do nível municipal.")
    # Exemplo de inspeção para um estado, se precisar investigar:
    # print(df_completo[(df_completo['UF'] == 'SP') & (df_completo['Ano'] == 2023) & (df_completo['Rede'] == 'Total') & (df_completo['Localizacao'] == 'Total')][['UF', 'Nome_Municipio', 'Codigo_Municipio']].drop_duplicates().head(20))
    exit()

print("\n--- Dados Filtrados para Visualização (Ensino Médio - MG, SP, RJ - 2023) ---")
colunas_ensino_medio = ['UF', 'Taxa_Aprovacao_Ensino_Medio', 'Taxa_Reprovacao_Ensino_Medio', 'Taxa_Abandono_Ensino_Medio']
print(df_filtrado[colunas_ensino_medio])

# Renomear colunas para facilitar o uso nos gráficos (foco no Ensino Médio)
df_plot = df_filtrado.rename(columns={
    'Taxa_Aprovacao_Ensino_Medio': 'Aprovação (EM)',
    'Taxa_Reprovacao_Ensino_Medio': 'Reprovação (EM)',
    'Taxa_Abandono_Ensino_Medio': 'Abandono (EM)'
})[['UF', 'Aprovação (EM)', 'Reprovação (EM)', 'Abandono (EM)']]


# --- 3. Criação das Visualizações Interativas com Plotly ---

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

# Visualização 2: Gráfico de Barras Empilhadas
# Mostrando a composição das taxas (Aprovação, Reprovação, Abandono) para cada estado.
if not df_plot.empty:
    fig2 = go.Figure()
    cores = {'Aprovação (EM)': 'rgb(76,175,80)', 'Reprovação (EM)': 'rgb(255,152,0)', 'Abandono (EM)': 'rgb(244,67,54)'}

    for metrica, nome in zip(metricas, nomes_legenda):
        if metrica in df_plot.columns:
             fig2.add_trace(go.Bar(
                name=nome,
                x=df_plot['UF'],
                y=df_plot[metrica],
                marker_color=cores.get(metrica),
                text=df_plot[metrica].apply(lambda x: f'{x:.1f}%'),
                textposition='auto'
            ))
        else:
            print(f"Aviso V2: Coluna '{metrica}' não encontrada para o gráfico de barras empilhadas.")


    fig2.update_layout(
        barmode='stack',
        title_text='<b>Composição das Taxas de Rendimento do Ensino Médio (MG, SP, RJ) - 2023</b><br><i>Fonte: INEP (Dataset Kaggle)</i>',
        xaxis_title='Estado',
        yaxis_title='Taxa Acumulada (%)',
        legend_title_text='Métricas do Ensino Médio',
        yaxis_ticksuffix="%"
    )
    print("\nExibindo Gráfico 2: Barras Empilhadas...")
    fig2.show()
else:
    print("Não há dados para gerar o Gráfico 2.")

# Visualização 3: Múltiplos Gráficos de Pizza (Donut)
# Um para cada estado, mostrando a proporção das taxas no Ensino Médio.
if not df_plot.empty and 'UF' in df_plot.columns:
    estados_presentes = df_plot['UF'].unique()
    num_estados = len(estados_presentes)

    if num_estados > 0:
        # Define o número de colunas para os subplots (máximo 3 por linha, por exemplo)
        cols_subplot = min(num_estados, 3)
        rows_subplot = (num_estados - 1) // cols_subplot + 1

        fig3 = make_subplots(
            rows=rows_subplot, cols=cols_subplot,
            specs=[[{'type':'domain'}] * cols_subplot] * rows_subplot, # 'domain' para pie charts
            subplot_titles=[f"<b>{estado}</b>" for estado in estados_presentes]
        )

        labels_pizza = ['Aprovação', 'Reprovação', 'Abandono']

        for i, estado in enumerate(estados_presentes):
            row_idx = (i // cols_subplot) + 1
            col_idx = (i % cols_subplot) + 1

            estado_data = df_plot[df_plot['UF'] == estado].iloc[0]
            valores_pizza = []
            if 'Aprovação (EM)' in estado_data: valores_pizza.append(estado_data['Aprovação (EM)'])
            if 'Reprovação (EM)' in estado_data: valores_pizza.append(estado_data['Reprovação (EM)'])
            if 'Abandono (EM)' in estado_data: valores_pizza.append(estado_data['Abandono (EM)'])

            if len(valores_pizza) == 3: # Certifica que temos os 3 valores
                fig3.add_trace(go.Pie(
                    labels=labels_pizza,
                    values=valores_pizza,
                    name=estado,
                    hole=.4, # Para efeito Donut
                    hoverinfo='label+percent+value',
                    textinfo='percent+label',
                    marker_colors=[cores['Aprovação (EM)'], cores['Reprovação (EM)'], cores['Abandono (EM)']]
                ), row=row_idx, col=col_idx)
            else:
                print(f"Aviso V3: Dados incompletos para o gráfico de pizza do estado {estado}.")


        fig3.update_layout(
            title_text='<b>Distribuição Percentual das Taxas do Ensino Médio por Estado - 2023</b><br><i>Fonte: INEP (Dataset Kaggle)</i>',
            showlegend=False # Legenda já está nos próprios gráficos de pizza
        )
        print("\nExibindo Gráfico 3: Múltiplos Gráficos de Pizza/Donut...")
        fig3.show()
    else:
        print("Não há estados suficientes nos dados filtrados para gerar o Gráfico 3.")
else:
    print("Não há dados para gerar o Gráfico 3.")

print("\n--- Análise e Visualização Concluídas ---")
print("Os gráficos interativos devem ter sido abertos no seu navegador padrão.")
print("Passe o mouse sobre os gráficos para ver detalhes e interagir.")

