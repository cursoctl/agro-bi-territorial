# Agro BI Territorial — starter kit para WSL

Projeto demonstrativo com dados fictícios para PostgreSQL e Power BI.

## Requisitos
- WSL 2 (Ubuntu recomendado)
- Docker Desktop com integração WSL, ou Docker Engine instalado no WSL
- Python 3.10+
- Power BI Desktop para construir o relatório (normalmente executado no Windows)

## 1. Subir o banco
Na pasta do projeto:

```bash
cp .env.example .env
docker compose up -d
docker compose ps
```

## 2. Preparar Python e dependências
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Criar as tabelas
```bash
python scripts/run_sql.py sql/01_schema/01_create_schema.sql
```

## 4. Carregar os CSVs
```bash
python scripts/load_csv.py
```
A carga usa `ON CONFLICT DO NOTHING`, então é possível reexecutar para ignorar IDs já existentes. Para reiniciar completamente o ambiente de demonstração, remova o volume do banco com `docker compose down -v` e suba novamente; isso apaga os dados do volume local.

## 5. Criar views e validar qualidade
```bash
python scripts/run_sql.py sql/02_views/01_powerbi_views.sql
psql "postgresql://agro_user:agro_local_dev@localhost:5432/agro_bi" -f sql/03_quality/01_quality_checks.sql
```
Se `psql` não estiver instalado no WSL, use um cliente SQL ou execute as consultas no Power BI/pgAdmin.

## 6. Conectar o Power BI
1. No Power BI Desktop, escolha **Obter dados > PostgreSQL**.
2. Servidor: `localhost:5432`; banco: `agro_bi`.
3. Selecione o esquema `agro` e importe as views `vw_plantio_analitico`, `vw_custos_por_categoria` e `vw_aplicacoes_analiticas`; importe também dimensões para filtros e mapas.
4. Importe `powerbi/theme.json` em **Exibir > Temas > Procurar temas**.
5. Copie as medidas de `powerbi/dax_measures.dax` para a tabela de medidas ou adapte os nomes ao modelo importado.
6. Para o mapa, use latitude/longitude de `dim_talhao`; classifique as colunas como Latitude e Longitude no Power BI.

## Estrutura
- `data/raw/`: CSVs de demonstração.
- `sql/01_schema/`: tabelas e índices.
- `sql/02_views/`: views para consumo analítico.
- `sql/03_quality/`: verificações de qualidade.
- `scripts/`: execução de SQL e carga CSV.
- `powerbi/`: medidas DAX e tema.
- `docs/modelagem.md`: grão, relacionamentos e ressalvas.

## Limites conhecidos
Este kit não contém um arquivo `.pbix` pronto nem polígonos geoespaciais oficiais. Ele prepara a camada de dados e os artefatos para construir o relatório. Use dados autorizados e valide definições agronômicas antes de qualquer decisão operacional.
