import duckdb
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / "data" / "imdb_unseen.parquet"

con = duckdb.connect()

con.execute(f"""
    CREATE TABLE IF NOT EXISTS imdb_unseen AS
    SELECT * FROM read_parquet('{path}')
""")

def get_unseen_movies(
    genre = None,
    ano_min = 1900,
    ano_max = 2024,
    duracao_min = 60,
    duracao_max = 240,
    nota_min = 0,
    votos_min = 0,
    limite = 10
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

def sortear_filme(genero=None, nota_min=7.0, votos_min=10000):
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