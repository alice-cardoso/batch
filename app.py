import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import os
import tempfile

def carregar_arquivo_xml(conteudo_arquivo, nome_arquivo):
    conteudo = conteudo_arquivo.decode('utf-8')

    if '<ConfiguracaoBatch>' not in conteudo:
        conteudo = f"<ConfiguracaoBatch>{conteudo}</ConfiguracaoBatch>"

    try:
        root = ET.fromstring(conteudo)
    except ET.ParseError:
        return []

    dados = []
    nome_arquivo = os.path.splitext(nome_arquivo)[0]

    for emissor in root.findall('Emissor'):
        nome = emissor.findtext('NomeBase', default='N/A')
        servidor = emissor.findtext('Servidor', default='N/A')
        horario = emissor.findtext('HoraExecucao', default='N/A')
        dados.append([nome, servidor, horario, nome_arquivo])

    return dados

def consolidar_planilhas(arquivos):
    todos_dados = []

    for arquivo in arquivos:
        dados = carregar_arquivo_xml(arquivo.read(), arquivo.name)
        todos_dados.extend(dados)

    if not todos_dados:
        return None

    df = pd.DataFrame(todos_dados, columns=[
        'Emissor', 'Servidor', 'Horário de Inicio', 'Host Batch'])

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(temp_file.name, index=False)
    return temp_file.name

st.set_page_config(page_title="Consolidador XML", layout="centered")
st.markdown("<h1 style='white-space: nowrap;'>📁 Gerador do Controle de Batches</h1>", unsafe_allow_html=True)

st.write("Selecione os arquivos que serão consolidados:")

uploaded_files = st.file_uploader(
    " ", type=["txt", "xml"], accept_multiple_files=True)

if st.button("Enviar"):
    if not uploaded_files:
        st.warning("Por favor, envie ao menos um arquivo.")
    else:
        caminho_saida = consolidar_planilhas(uploaded_files)
        if caminho_saida:
            with open(caminho_saida, "rb") as file:
                st.success("✅ Arquivos consolidados e salvos com sucesso!")
                st.download_button(
                    label="📥 Baixar Planilha Consolidada",
                    data=file,
                    file_name="Consolidado_Batch.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.error("❌ Falha ao processar os arquivos. Verifique o conteúdo.")