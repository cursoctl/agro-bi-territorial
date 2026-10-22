import os
import sys
import logging
from pathlib import Path
import psycopg
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Agro_Test_Pipeline")

def rodar_teste():
    base_dir = Path(__file__).resolve().parent.parent
    load_dotenv(base_dir / ".env")
    
    # Lendo as variáveis mapeadas do nosso .env seguro
    db_host = os.getenv("PGHOST", "127.0.0.1")
    db_port = os.getenv("PGPORT", "5436")
    db_name = os.getenv("PGDATABASE", "agro_bi")
    db_user = os.getenv("PGUSER", "agro_user")
    db_pass = os.getenv("PGPASSWORD", "agro_local_dev")
    
    logger.info(f"Conectando ao PostGIS na porta isolada: {db_port}")
    
    try:
        with psycopg.connect(
            host=db_host, port=db_port, dbname=db_name,
            user=db_user, password=db_pass, autocommit=True
        ) as conn:
            with conn.cursor() as cur:
                # -------------------------------------------------------------------------
                # 1. CRIAÇÃO DO SCHEMA E TABELAS (DDL)
                # -------------------------------------------------------------------------
                logger.info("Criando tabelas relacionais do Star Schema...")
                cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
                
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dim_fazenda (id_fazenda INT PRIMARY KEY, nome_fazenda VARCHAR(100), municipio VARCHAR(100));
                    CREATE TABLE IF NOT EXISTS dim_talhao (id_talhao INT PRIMARY KEY, id_fazenda INT, codigo_talhao VARCHAR(50), area_ha NUMERIC(10,2));
                    CREATE TABLE IF NOT EXISTS dim_safra (id_safra INT PRIMARY KEY, nome_safra VARCHAR(50));
                    CREATE TABLE IF NOT EXISTS dim_cultura (id_cultura INT PRIMARY KEY, nome_cultura VARCHAR(50));
                    CREATE TABLE IF NOT EXISTS fato_colheita (id_colheita SERIAL PRIMARY KEY, id_talhao INT, id_safra INT, id_cultura INT, producao_sc NUMERIC(10,2), area_colhida_ha NUMERIC(10,2));
                """)
                
                # -------------------------------------------------------------------------
                # 2. INGESTÃO DE DADOS FICTÍCIOS (DML) - Evitando chaves duplicadas
                # -------------------------------------------------------------------------
                logger.info("Injetando registros de teste nas tabelas fato e dimensões...")
                cur.execute("INSERT INTO dim_fazenda VALUES (1, 'Fazenda Pampa BI', 'Pelotas') ON CONFLICT DO NOTHING;")
                cur.execute("INSERT INTO dim_talhao VALUES (101, 1, 'Talhão Norte 01', 150.00) ON CONFLICT DO NOTHING;")
                cur.execute("INSERT INTO dim_safra VALUES (1, 'Safra 2025/26') ON CONFLICT DO NOTHING;")
                cur.execute("INSERT INTO dim_cultura VALUES (1, 'Soja') ON CONFLICT DO NOTHING;")
                
                # Injeta a produção fictícia (Ex: 9.000 sacas colhidas em 150 hectares = 60 sc/ha)
                cur.execute("INSERT INTO fato_colheita (id_talhao, id_safra, id_cultura, producao_sc, area_colhida_ha) VALUES (101, 1, 1, 9000.00, 150.00);")
                
                # -------------------------------------------------------------------------
                # 3. CRIAÇÃO DA VIEW ANALÍTICA PARA O POWER BI
                # -------------------------------------------------------------------------
                logger.info("Construindo a camada de abstração (Views SQL)...")
                cur.execute("""
                    CREATE OR REPLACE VIEW vw_powerbi_produtividade AS
                    SELECT 
                        f.nome_fazenda, f.municipio, s.nome_safra, c.nome_cultura, t.codigo_talhao, t.area_ha,
                        fc.producao_sc, fc.area_colhida_ha,
                        ROUND(fc.producao_sc / NULLIF(fc.area_colhida_ha, 0), 2) AS produtividade_sc_ha
                    FROM fato_colheita fc
                    JOIN dim_talhao t ON fc.id_talhao = t.id_talhao
                    JOIN dim_fazenda f ON t.id_fazenda = f.id_fazenda
                    JOIN dim_safra s ON fc.id_safra = s.id_safra
                    JOIN dim_cultura c ON fc.id_cultura = c.id_cultura;
                """)
                
                logger.info("🚀 PIPELINE EXECUTADO COM SUCESSO DE PONTA A PONTA!")
                
    except Exception as e:
        logger.error(f"Erro crítico na execução do banco: {str(e)}")

if __name__ == "__main__":
    rodar_teste()

