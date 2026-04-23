import streamlit as st
import requests
import os
from queries import get_unseen_movies, sortear_filme,listar_generos,get_movie_info,user_recommendations

st.set_page_config(page_title="Movie Picker", page_icon="🎬", layout="wide")
st.title("Movie Picker 🎬")


generos =  ["Todos"] + listar_generos()["genre"].tolist()

def exibir_poster(row):
    poster_url,sinopse =  get_movie_info(row["primaryTitle"],row["startYear"])

    with st.container(border=True):
        st.image(poster_url, use_container_width=True)
        st.markdown(f"**{row['primaryTitle']}** ({row['startYear']})")
        st.caption(f"{row['genres']}")
        st.caption(f"{row['runtimeMinutes']} min · {row['averageRating']}")
        with st.expander("Sinopse"):
            st.write(sinopse)

with st.sidebar:
    st.header("Filtros")
    genero = st.selectbox("Gênero", generos)
    ano = st.slider("Ano de lançamento", 1900, 2024, (2000, 2024))
    duracao = st.slider("Duraçao (minutos)",60,240,(60,180))
    nota = st.slider("Nota mínima",0.0,10.0,7.0,0.1)
    limite = st.slider("Número de filmes a exibir",1,20,10)

    st.divider()

    use_recomendations = st.checkbox("Gerar recomendações personalizadas")

genero_filtro = None if genero == "Todos" else genero

if st.button("Sortear um filme"):
    filme = sortear_filme(genero=genero_filtro, nota_min=nota)
    if not filme.empty:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col3:
            exibir_poster(filme.iloc[0])
    else:
        st.warning("Nenhum filme encontrado com os filtros selecionados.")
        
st.divider()

st.subheader("Filmes Sugeridos")

if use_recomendations:
    with st.spinner("Gerando recomendações personalizadas..."):
        filmes = user_recommendations()
        if filmes.empty:
            st.info("Não foi possível gerar recomendações personalizadas. Ajuste seus filtros ou tente novamente mais tarde.")
        else:
            cols = st.columns(5)
            for i, (_, row) in enumerate(filmes.iterrows()):
                with cols[i % 5]:
                    exibir_poster(row)
else:
    filmes = get_unseen_movies(
        genre=genero_filtro,
        ano_min=ano[0],ano_max=ano[1],
        duracao_min=duracao[0],duracao_max=duracao[1],
        nota_min=nota,
    limite=limite
)

if not filmes.empty:
    cols = st.columns(5)
    for i, (_, row) in enumerate(filmes.iterrows()):
        with cols[i % 5]:
            exibir_poster(row)
else:
    st.info("Ajuste os filtros para ver mais opções.")
