CREATE SCHEMA IF NOT EXISTS agro;
SET search_path TO agro, public;

-- Ativa a extensão espacial do PostGIS (Isso mostra que você é do Geoprocessamento!)
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS dim_fazenda (
    fazenda_id       INTEGER PRIMARY KEY,
    nome_fazenda     TEXT NOT NULL,
    municipio        TEXT NOT NULL,
    uf               CHAR(2) NOT NULL,
    area_total_ha    NUMERIC(12,2) NOT NULL CHECK (area_total_ha > 0)
);

CREATE TABLE IF NOT EXISTS dim_talhao (
    talhao_id        INTEGER PRIMARY KEY,
    fazenda_id       INTEGER NOT NULL REFERENCES dim_fazenda(fazenda_id),
    codigo_talhao    TEXT NOT NULL,
    area_ha          NUMERIC(12,2) NOT NULL CHECK (area_ha > 0),
    latitude         NUMERIC(9,6),
    longitude        NUMERIC(9,6),
    -- COLUNA GEOMÉTRICA DO POSTGIS: Armazena o ponto central do talhão em WGS 84
    geom             geometry(Point, 4326),
    UNIQUE (fazenda_id, codigo_talhao),
    CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180)
);

-- O resto das tabelas continua igual ao que você já montou...

-- ÍNDICE ESPACIAL GIST: Crucial para o Power BI ler a geografia de forma instantânea
CREATE INDEX IF NOT EXISTS ix_talhao_geom ON dim_talhao USING GIST(geom);


CREATE TABLE IF NOT EXISTS dim_cultura (
    cultura_id       INTEGER PRIMARY KEY,
    nome_cultura     TEXT NOT NULL UNIQUE,
    unidade_producao TEXT NOT NULL DEFAULT 't'
);

CREATE TABLE IF NOT EXISTS dim_safra (
    safra_id         INTEGER PRIMARY KEY,
    nome_safra       TEXT NOT NULL UNIQUE,
    data_inicio      DATE NOT NULL,
    data_fim         DATE NOT NULL,
    CHECK (data_fim >= data_inicio)
);

CREATE TABLE IF NOT EXISTS dim_insumo (
    insumo_id        INTEGER PRIMARY KEY,
    nome_insumo      TEXT NOT NULL,
    categoria        TEXT NOT NULL,
    unidade          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fato_plantio (
    plantio_id       INTEGER PRIMARY KEY,
    talhao_id        INTEGER NOT NULL REFERENCES dim_talhao(talhao_id),
    cultura_id       INTEGER NOT NULL REFERENCES dim_cultura(cultura_id),
    safra_id         INTEGER NOT NULL REFERENCES dim_safra(safra_id),
    data_plantio     DATE NOT NULL,
    area_plantada_ha NUMERIC(12,2) NOT NULL CHECK (area_plantada_ha > 0)
);

CREATE TABLE IF NOT EXISTS fato_colheita (
    colheita_id      INTEGER PRIMARY KEY,
    plantio_id       INTEGER NOT NULL REFERENCES fato_plantio(plantio_id),
    data_colheita    DATE NOT NULL,
    producao_t       NUMERIC(14,3) NOT NULL CHECK (producao_t >= 0)
);

CREATE TABLE IF NOT EXISTS fato_aplicacao (
    aplicacao_id     INTEGER PRIMARY KEY,
    plantio_id       INTEGER NOT NULL REFERENCES fato_plantio(plantio_id),
    insumo_id        INTEGER NOT NULL REFERENCES dim_insumo(insumo_id),
    data_aplicacao   DATE NOT NULL,
    quantidade       NUMERIC(14,3) NOT NULL CHECK (quantidade >= 0),
    custo_total      NUMERIC(14,2) NOT NULL CHECK (custo_total >= 0)
);

CREATE TABLE IF NOT EXISTS fato_custos (
    custo_id         INTEGER PRIMARY KEY,
    plantio_id       INTEGER NOT NULL REFERENCES fato_plantio(plantio_id),
    data_lancamento  DATE NOT NULL,
    categoria_custo  TEXT NOT NULL,
    valor            NUMERIC(14,2) NOT NULL CHECK (valor >= 0)
);

CREATE TABLE IF NOT EXISTS fato_previsao (
    previsao_id          INTEGER PRIMARY KEY,
    plantio_id           INTEGER NOT NULL REFERENCES fato_plantio(plantio_id),
    data_previsao        DATE NOT NULL,
    producao_prevista_t  NUMERIC(14,3) NOT NULL CHECK (producao_prevista_t >= 0),
    confianca_pct        NUMERIC(5,2) CHECK (confianca_pct BETWEEN 0 AND 100)
);

CREATE INDEX IF NOT EXISTS ix_talhao_fazenda ON dim_talhao(fazenda_id);
CREATE INDEX IF NOT EXISTS ix_plantio_talhao ON fato_plantio(talhao_id);
CREATE INDEX IF NOT EXISTS ix_plantio_safra ON fato_plantio(safra_id);
CREATE INDEX IF NOT EXISTS ix_colheita_plantio ON fato_colheita(plantio_id);
CREATE INDEX IF NOT EXISTS ix_custos_plantio ON fato_custos(plantio_id);
