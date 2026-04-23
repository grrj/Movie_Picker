import streamlit as st
from queries import get_unseen_movies, sortear_filme,listar_generos

st.title("Movie Picker 🎬")

generos =  ["Todos"] + listar_generos()["genre"].tolist()

with st.sidebar:
    genero = st.selectbox("Gênero", generos)
    ano = st.slider("Ano de lançamento", 1900, 2024, (2000, 2024))
    duracao = st.slider("Duraçao (minutos)",60,240,(60,180))
    nota = st.slider("Nota mínima",0.0,10.0,7.0,0.1)
    votos = st.slider("Número mínimo de votos",0,1000000,10000,1000)
    limite = st.slider("Número de filmes a exibir",1,20,10)

genero_filtro = None if genero == "Todos" else genero

if st.button("Sortear um filme"):
    filme = sortear_filme(genero=genero_filtro,nota_min=nota,votos_min=votos)
    if not filme.empty:
        st.subheader(f"{filme.iloc[0]['primaryTitle']} ({filme.iloc[0]['startYear']})")
        st.write(f"**Gêneros:** {filme.iloc[0]['genres']}")
        st.write(f"**Duração:** {filme.iloc[0]['runtimeMinutes']} minutos")
        st.write(f"**Nota:** {filme.iloc[0]['averageRating']}")
    else:
        st.warning("Nenhum filme encontrado com os filtros selecionados.")

st.divider()

filmes = get_unseen_movies(
    genre=genero_filtro,
    ano_min=ano[0],ano_max=ano[1],
    duracao_min=duracao[0],duracao_max=duracao[1],
    nota_min=nota,
    votos_min=votos,
    limite=limite
)

st.dataframe(filmes,use_container_width=True)

