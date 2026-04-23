import duckdb
from pathlib import Path  

ROOT = Path(__file__).resolve().parent

def rodar_pipeline():
    path_b = ROOT / "data" / "title.basics.tsv"
    path_r = ROOT / "data" / "title.ratings.tsv"
    path_w = ROOT / "data" / "watched.csv"
    path_out = ROOT / "data" / "imdb_unseen.parquet"

    con = duckdb.connect()

    con.execute(f"""
        CREATE TABLE imdb AS
        SELECT
            b.tconst,
            b.primaryTitle,
            b.originalTitle,
            b.startYear,
            b.genres,
            b.runtimeMinutes,
            r.averageRating,
            r.numVotes
        FROM read_csv('{path_b}', delim='\t', nullstr='\\N') AS b
        LEFT JOIN read_csv('{path_r}', delim='\t', nullstr='\\N')
            ON b.tconst = r.tconst
        WHERE b.titleType = 'movie' AND b.isAdult = '0'
    """)

    con.execute(f"""
        CREATE TABLE imdb_unseen AS
        SELECT i.*
        FROM imdb i
        LEFT JOIN read_csv('{path_w}', delim=',') w
            ON (
                LOWER(TRIM(i.primaryTitle)) = LOWER(TRIM(w.Name))
                OR
                LOWER(TRIM(i.originalTitle)) = LOWER(TRIM(w.Name))
            )
        AND TRY_CAST(i.startYear AS INTEGER) = w.Year
        WHERE w.Name IS NULL
    """)

    con.execute(f"""
        ALTER TABLE imdb_unseen
        ALTER COLUMN startYear TYPE INTEGER
        USING TRY_CAST(startYear AS INTEGER)
    """)

    con.execute(f"""
        ALTER TABLE imdb_unseen
        ALTER COLUMN runtimeMinutes TYPE INTEGER
        USING TRY_CAST(runtimeMinutes AS INTEGER)
    """)

    con.execute(f"""COPY imdb_unseen TO '{path_out}' (FORMAT 'parquet')""")
    con.close()
