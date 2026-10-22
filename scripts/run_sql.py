import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

def main():
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python scripts/run_sql.py caminho/do/arquivo.sql")
    sql_path = (ROOT / sys.argv[1]).resolve()
    if not sql_path.is_file():
        raise SystemExit(f"Arquivo não encontrado: {sql_path}")
        
    conninfo = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": os.getenv("PGPORT", "5433"), # Fallback padrão alterado para a nossa porta segura 5433
        "dbname": os.getenv("PGDATABASE", "agro_bi"),
        "user": os.getenv("PGUSER", "agro_user"),
        "password": os.getenv("PGPASSWORD", "agro_local_dev"),
    }
    
    # AJUSTE CHAVE DE DEVSECOPS: Usamos autocommit=True para liberar comandos DDL e extensões PostGIS
    with psycopg.connect(**conninfo, autocommit=True) as conn:
        with conn.cursor() as cur:
            print(f"Conectado ao PostGIS na porta {conninfo['port']}. Executando script...")
            cur.execute(sql_path.read_text(encoding="utf-8"))
            
    print(f"Executado com sucesso: {sql_path.relative_to(ROOT)}")

if __name__ == "__main__":
    main()

