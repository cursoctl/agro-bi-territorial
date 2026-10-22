import os
import csv
import logging
from pathlib import Path
from dotenv import load_dotenv
import psycopg

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CSV_Loader")

def carregar_tabela(cur, caminho_csv, query_insert):
    """Lê um arquivo CSV local e executa a query de carga."""
    caminho = ROOT / caminho_csv
    if not caminho.is_file():
        logger.warning(f"Arquivo CSV não encontrado: {caminho_csv}")
        return

    logger.info(f"Processando arquivo: {caminho_csv}...")
    with open(caminho, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) # Pula o cabeçalho de colunas

        for row in reader:
            # PULO DO GATO CYBER: Se for o talhão, duplicamos a long (row[5]) e lat (row[4]) no fim do array
            if "dim_talhao.csv" in caminho_csv:
                # row[5] = longitude (X) | row[4] = latitude (Y)
                dados_parametros = row + [row[5], row[4]]
            else:
                dados_parametros = row
                
            # Executa o insert passando o array com a contagem exata de placeholders
            cur.execute(query_insert, dados_parametros)


def main():
    conninfo = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": os.getenv("PGPORT", "5434"),
        "dbname": os.getenv("PGDATABASE", "agro_bi"),
        "user": os.getenv("PGUSER", "agro_user"),
        "password": os.getenv("PGPASSWORD", "agro_local_dev"),
    }
    
    # Lista de dicionários mapeando os arquivos brutos e os comandos INSERT com UPSERT seguro
        # Lista de dicionários mapeando os arquivos brutos e os comandos INSERT com marcadores posicionais ($1, $2)
        # Lista corrigida mantendo o padrão %s do psycopg3 para todas as tabelas
    carga_jobs = [
        # 1. CARGA DAS DIMENSÕES (Star Schema Base)
        {
            "csv": "data/raw/dim_fazenda.csv",
            "sql": """INSERT INTO agro.dim_fazenda (fazenda_id, nome_fazenda, municipio, uf, area_total_ha)
                      VALUES (%s, %s, %s, %s, %s) ON CONFLICT (fazenda_id) DO NOTHING;"""
        },
        {
            "csv": "data/raw/dim_talhao.csv",
            # SOLUÇÃO REAL: Passamos apenas 6 placeholders (%s). O PostGIS monta o ponto lendo as duas últimas colunas numéricas nativas da linha.
            "sql": """INSERT INTO agro.dim_talhao (talhao_id, fazenda_id, codigo_talhao, area_ha, latitude, longitude, geom)
                      VALUES (%s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s::numeric, %s::numeric), 4326))
                      ON CONFLICT (talhao_id) DO NOTHING;"""
        },
        {
            "csv": "data/raw/dim_cultura.csv",
            "sql": """INSERT INTO agro.dim_cultura (cultura_id, nome_cultura, unidade_producao)
                      VALUES (%s, %s, %s) ON CONFLICT (cultura_id) DO NOTHING;"""
        },
        {
            "csv": "data/raw/dim_safra.csv",
            "sql": """INSERT INTO agro.dim_safra (safra_id, nome_safra, data_inicio, data_fim)
                      VALUES (%s, %s, %s, %s) ON CONFLICT (safra_id) DO NOTHING;"""
        },
        {
            "csv": "data/raw/dim_insumo.csv",
            "sql": """INSERT INTO agro.dim_insumo (insumo_id, nome_insumo, categoria, unidade)
                      VALUES (%s, %s, %s, %s) ON CONFLICT (insumo_id) DO NOTHING;"""
        },
        # 2. CARGA DAS TABELAS FATO (Métricas e Eventos)
        {
            "csv": "data/raw/fato_plantio.csv",
            "sql": """INSERT INTO agro.fato_plantio (plantio_id, talhao_id, cultura_id, safra_id, data_plantio, area_plantada_ha)
                      VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (plantio_id) DO NOTHING;"""
        },
        {
            "csv": "data/raw/fato_colheita.csv",
            "sql": """INSERT INTO agro.fato_colheita (colheita_id, plantio_id, data_colheita, producao_t)
                      VALUES (%s, %s, %s, %s) ON CONFLICT (colheita_id) DO NOTHING;"""
        },
        {
            "csv": "data/raw/fato_aplicacao.csv",
            "sql": """INSERT INTO agro.fato_aplicacao (aplicacao_id, plantio_id, insumo_id, data_aplicacao, quantidade, custo_total)
                      VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (aplicacao_id) DO NOTHING;"""
        },
        {
            "csv": "data/raw/fato_custos.csv",
            "sql": """INSERT INTO agro.fato_custos (custo_id, plantio_id, data_lancamento, categoria_custo, valor)
                      VALUES (%s, %s, %s, %s, %s) ON CONFLICT (custo_id) DO NOTHING;"""
        },
        {
            "csv": "data/raw/fato_previsao.csv",
            "sql": """INSERT INTO agro.fato_previsao (previsao_id, plantio_id, data_previsao, producao_prevista_t, confianca_pct)
                      VALUES (%s, %s, %s, %s, %s) ON CONFLICT (previsao_id) DO NOTHING;"""
        }
    ]


    
    try:
        with psycopg.connect(**conninfo) as conn:
            with conn.cursor() as cur:
                logger.info("Iniciando transação de ingestão do pipeline de dados...")
                
                # Seta o search_path para o schema do projeto
                cur.execute("SET search_path TO agro, public;")
                
                for job in carga_jobs:
                    carregar_tabela(cur, job["csv"], job["sql"])
                    
                conn.commit()
                logger.info("🏆 Todos os arquivos CSV de demonstração foram ingeridos com sucesso!")
                
    except Exception as e:
        logger.error(f"Erro crítico durante a carga dos dados no pipeline: {str(e)}")

if __name__ == "__main__":
    main()

