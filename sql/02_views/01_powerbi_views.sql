CREATE OR REPLACE VIEW agro.vw_plantio_analitico AS
SELECT
    p.plantio_id,
    f.fazenda_id, f.nome_fazenda, f.municipio, f.uf,
    t.talhao_id, t.codigo_talhao, t.area_ha AS area_talhao_ha,
    c.cultura_id, c.nome_cultura,
    s.safra_id, s.nome_safra,
    p.data_plantio, p.area_plantada_ha,
    COALESCE(ch.producao_t, 0) AS producao_t,
    CASE WHEN p.area_plantada_ha > 0
         THEN ch.producao_t / p.area_plantada_ha
         ELSE NULL END AS produtividade_t_ha,
    COALESCE(cu.custo_total, 0) AS custo_total,
    CASE WHEN p.area_plantada_ha > 0
         THEN cu.custo_total / p.area_plantada_ha
         ELSE NULL END AS custo_por_ha,
    COALESCE(pr.producao_prevista_t, 0) AS producao_prevista_t,
    pr.confianca_pct
FROM agro.fato_plantio p
JOIN agro.dim_talhao t ON t.talhao_id = p.talhao_id
JOIN agro.dim_fazenda f ON f.fazenda_id = t.fazenda_id
JOIN agro.dim_cultura c ON c.cultura_id = p.cultura_id
JOIN agro.dim_safra s ON s.safra_id = p.safra_id
LEFT JOIN (
    SELECT plantio_id, SUM(producao_t) AS producao_t
    FROM agro.fato_colheita GROUP BY plantio_id
) ch ON ch.plantio_id = p.plantio_id
LEFT JOIN (
    SELECT plantio_id, SUM(valor) AS custo_total
    FROM agro.fato_custos GROUP BY plantio_id
) cu ON cu.plantio_id = p.plantio_id
LEFT JOIN (
    SELECT DISTINCT ON (plantio_id) plantio_id, producao_prevista_t, confianca_pct
    FROM agro.fato_previsao
    ORDER BY plantio_id, data_previsao DESC, previsao_id DESC
) pr ON pr.plantio_id = p.plantio_id;

CREATE OR REPLACE VIEW agro.vw_custos_por_categoria AS
SELECT
    p.plantio_id, f.fazenda_id, f.nome_fazenda, t.talhao_id,
    c.nome_cultura, s.nome_safra, cu.categoria_custo,
    SUM(cu.valor) AS valor_custo
FROM agro.fato_custos cu
JOIN agro.fato_plantio p ON p.plantio_id = cu.plantio_id
JOIN agro.dim_talhao t ON t.talhao_id = p.talhao_id
JOIN agro.dim_fazenda f ON f.fazenda_id = t.fazenda_id
JOIN agro.dim_cultura c ON c.cultura_id = p.cultura_id
JOIN agro.dim_safra s ON s.safra_id = p.safra_id
GROUP BY p.plantio_id, f.fazenda_id, f.nome_fazenda, t.talhao_id,
         c.nome_cultura, s.nome_safra, cu.categoria_custo;

CREATE OR REPLACE VIEW agro.vw_aplicacoes_analiticas AS
SELECT
    a.aplicacao_id, a.plantio_id, a.data_aplicacao,
    i.insumo_id, i.nome_insumo, i.categoria, i.unidade,
    a.quantidade, a.custo_total,
    f.fazenda_id, f.nome_fazenda, t.talhao_id, t.codigo_talhao,
    c.nome_cultura, s.nome_safra
FROM agro.fato_aplicacao a
JOIN agro.dim_insumo i ON i.insumo_id = a.insumo_id
JOIN agro.fato_plantio p ON p.plantio_id = a.plantio_id
JOIN agro.dim_talhao t ON t.talhao_id = p.talhao_id
JOIN agro.dim_fazenda f ON f.fazenda_id = t.fazenda_id
JOIN agro.dim_cultura c ON c.cultura_id = p.cultura_id
JOIN agro.dim_safra s ON s.safra_id = p.safra_id;
