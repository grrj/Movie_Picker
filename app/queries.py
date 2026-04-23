import duckdb
from pathlib import Path
import streamlit as st
import requests

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / "data" / "imdb_unseen.parquet"
path_user = ROOT / "data" / "user_profile.parquet"

con = duckdb.connect()

con.execute(f"""
    CREATE TABLE IF NOT EXISTS imdb_unseen AS
    SELECT * FROM read_parquet('{path}')
""")

@st.cache_data
def get_unseen_movies(
    genre = None,
    ano_min = 1900,
    ano_max = 2024,
    duracao_min = 60,
    duracao_max = 240,
    nota_min = 0,
    limite = 10,
    votos_min = 10000
):
    filtros = [
        f"startYear BETWEEN {ano_min} AND {ano_max}",
        f"runtimeMinutes BETWEEN {duracao_min} AND {duracao_max}",
        f"averageRating >= {nota_min}",
        f"numVotes >= {votos_min}"
    ]
    if genre:
        filtros.append(f"genres LIKE '%{genre}%'")
    where = " AND ".join(filtros)

    return con.execute(f"""
        SELECT
            primaryTitle,
            originalTitle,
            startYear,
            genres,
            runtimeMinutes,
            averageRating,
            numVotes
        FROM imdb_unseen
        WHERE {where}
        ORDER BY averageRating DESC
        LIMIT {limite}
    """).fetchdf()
    
@st.cache_data
def sortear_filme(genero=None, nota_min=7.0,votos_min=10000):
    filtros = [
        f"averageRating >= {nota_min}",
        f"numVotes >= {votos_min}"
    ]
    if genero:
        filtros.append(f"genres LIKE '%{genero}%'")
    where = " AND ".join(filtros)

    return con.execute(f"""
        SELECT
            primaryTitle,
            originalTitle,
            startYear,
            genres,
            runtimeMinutes,
            averageRating,
            numVotes
        FROM imdb_unseen
        WHERE {where}
        ORDER BY RANDOM()
        LIMIT 1
    """).fetchdf()

@st.cache_data
def listar_generos():
    return con.execute("""
        SELECT DISTINCT TRIM(genre) AS genre
        FROM (
            SELECT UNNEST(STRING_SPLIT(genres,',')) AS genre
            FROM imdb_unseen
            WHERE genres IS NOT NULL
        )
        ORDER BY genre
    """).fetchdf()

@st.cache_data
def get_movie_info(titulo, ano):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": titulo,
        "year": ano,
        "language": "pt-BR"
    }

    try:
        res = requests.get(url, params=params).json()
        
       
        if "results" in res and len(res["results"]) > 0:
            
            
            movie = res["results"][0]
            
            poster_path = movie.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=Sem+Poster"
            
            overview = movie.get('overview', "Sem descrição disponível.")
            return poster_url, overview
        
    except Exception as e:
        
        st.error(f"Erro ao ligar à API: {e}")

    
    return "https://via.placeholder.com/500x750?text=Sem+Poster", "Sinopse não encontrada."

@st.cache_data(ttl=3600)
def user_recommendations():
    result = con.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'user_profile'").fetchone()
    if result[0] == 0:
        con.execute(f"""
            CREATE TABLE user_profile AS 
            SELECT * FROM read_parquet('{path_user}')
        """)
    query = """
    SELECT
        i.*,
        (
            CASE
                WHEN i.genres LIKE '%' || trim(split_part(p.top_genres, ',', 1)) || '%' THEN 5
                WHEN i.genres LIKE '%' || trim(split_part(p.top_genres, ',', 2)) || '%' THEN 3
                WHEN i.genres LIKE '%' || trim(split_part(p.top_genres, ',', 3)) || '%' THEN 2
                ELSE 0
            END +

            CASE
                WHEN (TRY_CAST(i.startYEAR AS INTEGER)/10)*10 = P.top_decade THEN 3
                ELSE 0
            END +

            CASE
                WHEN ABS(i.runtimeMinutes - P.avg_runtime) <= 20 THEN 2
                ELSE 0
            END
        ) AS recommendation_score
    FROM imdb_unseen i,user_profile p
    WHERE i.averageRating >= 7.0
        AND i.numVotes >= 10000
        AND i.startYear IS NOT NULL
        AND i.runtimeMinutes IS NOT NULL
    ORDER BY recommendation_score DESC, i.averageRating DESC
    LIMIT 50;
    """
    try:
        con.execute(f"""
        CREATE TABLE IF NOT EXISTS user_profile AS 
        SELECT * FROM read_parquet('{path_user}')
    """)
        result = con.execute(query).fetchdf()
        return result
    except Exception as e:
        st.error(f"Erro ao gerar recomendações: {e}")
        return con.execute("SELECT * FROM imdb_unseen LIMIT 0").fetchdf()
