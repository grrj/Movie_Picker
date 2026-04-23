# Movie Picker 🎬

App de recomendação de filmes baseado no seu histórico pessoal do Letterboxd, cruzado com o dataset público do IMDB.

> Acesse o app: [seu-usuario-movie-picker.streamlit.app](https://seu-usuario-movie-picker.streamlit.app)

---

## O problema

Escolher um filme para assistir é difícil quando você tem uma watchlist enorme e não quer assistir algo que já viu. Esse projeto resolve isso com dados reais — seus dados.

## Como funciona

1. Seus dados exportados do Letterboxd (`watched.csv`) são cruzados com o dataset público do IMDB
2. Um anti-join SQL exclui todos os filmes que você já assistiu
3. O app recomenda filmes que você ainda **não viu**, filtrados por gênero, nota, duração e ano
4. Um botão sorteia um filme aleatório com base nos filtros selecionados

---

## Arquitetura

```
movie-picker/
├── data/
│   ├── watched.csv                  ← exportado do Letterboxd
│   ├── watchlist.csv                ← exportado do Letterboxd
│   └── imdb_unseen.parquet          ← gerado pelo pipeline
├── app/
│   ├── pipeline.py                  ← pipeline de dados (DuckDB)
│   ├── queries.py                   ← lógica SQL isolada
│   └── app.py                       ← interface Streamlit
├── notebooks/
│   └── 01_ingestao_e_joins.ipynb    ← exploração e desenvolvimento do pipeline
├── requirements.txt
└── .gitignore
```

---

## Pipeline de dados

Construído com **DuckDB** rodando direto no Jupyter Notebook:

- Join entre `title.basics` (12 milhões de títulos) e `title.ratings` filtrando só filmes
- Anti-join com `watched.csv` usando `LOWER/TRIM` em título + ano para excluir filmes já assistidos
- Match por `primaryTitle` e `originalTitle` para cobrir títulos em outros idiomas
- Correção de tipos com `ALTER TABLE` — `startYear` e `runtimeMinutes` de `VARCHAR` para `INTEGER`
- Exportação da tabela final em **Parquet** para o app consumir

---

## Stack

| Camada | Tecnologia |
|---|---|
| Pipeline de dados | DuckDB + SQL |
| Notebook | Jupyter |
| Interface | Streamlit |
| Formato de dados | Parquet |
| Linguagem | Python |

---

## Como rodar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/movie-picker.git
cd movie-picker
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Adicione seus dados do Letterboxd

- Acesse seu perfil no Letterboxd → Settings → Import & Export → Export Your Data
- Coloque `watched.csv` e `watchlist.csv` na pasta `data/`

### 4. Rode o app

```bash
streamlit run app/app.py
```

Acesse `http://localhost:8501` no navegador.

> O `imdb_unseen.parquet` já está incluído no repositório — o app roda direto sem precisar reprocessar o dataset do IMDB.

---

## Como regenerar o parquet com seus próprios dados

Se quiser usar seu próprio histórico do Letterboxd do zero:

- Baixe `title.basics.tsv.gz` e `title.ratings.tsv` em [datasets.imdbws.com](https://datasets.imdbws.com)
- Coloque os arquivos na pasta `data/`
- Execute todas as células de `notebooks/01_ingestao_e_joins.ipynb`

---

## Decisões técnicas

**Por que DuckDB?**
Banco colunar que roda em memória — processa 12 milhões de linhas do IMDB sem nenhuma configuração externa. Ideal para pipelines locais e análise de dados.

**Por que separar `queries.py` do `app.py`?**
A lógica SQL isolada facilita a migração para fullstack. As funções do `queries.py` viram endpoints FastAPI praticamente sem mudança.

**Por que Parquet?**
Formato padrão de mercado para dados analíticos — compacto, tipado e lido nativamente pelo DuckDB. Separa o pipeline da aplicação.

---

## Próximos passos

- [ ] Enriquecer com posters e sinopses via TMDB API
- [ ] Incluir filtro por filmes da `watchlist.csv`
- [ ] Migrar para API FastAPI + frontend React

---

## Dados

Os datasets do IMDB são públicos e disponibilizados em [datasets.imdbws.com](https://datasets.imdbws.com) para uso não-comercial.
Os dados do Letterboxd são pessoais — cada usuário deve exportar os seus próprios para rodar o pipeline localmente.
