-- Cada consulta deve retornar zero linhas (ou valores explicáveis) para indicar qualidade.
-- 1. Plantios cuja área excede a área cadastrada do talhão.
SELECT p.plantio_id, t.codigo_talhao, p.area_plantada_ha, t.area_ha
FROM agro.fato_plantio p
JOIN agro.dim_talhao t ON t.talhao_id = p.talhao_id
WHERE p.area_plantada_ha > t.area_ha;

-- 2. Datas de colheita anteriores ao plantio.
SELECT ch.colheita_id, p.data_plantio, ch.data_colheita
FROM agro.fato_colheita ch
JOIN agro.fato_plantio p ON p.plantio_id = ch.plantio_id
WHERE ch.data_colheita < p.data_plantio;

-- 3. Registros sem correspondência (FKs já impedem a maioria dos casos).
SELECT 'plantio_sem_talhao' AS problema, p.plantio_id::text AS registro
FROM agro.fato_plantio p LEFT JOIN agro.dim_talhao t USING (talhao_id)
WHERE t.talhao_id IS NULL;

-- 4. Talhões com coordenadas ausentes para mapas.
SELECT talhao_id, codigo_talhao
FROM agro.dim_talhao
WHERE latitude IS NULL OR longitude IS NULL;

-- 5. Área plantada agregada por safra e cultura.
SELECT s.nome_safra, c.nome_cultura, SUM(p.area_plantada_ha) AS area_plantada_ha
FROM agro.fato_plantio p
JOIN agro.dim_safra s USING (safra_id)
JOIN agro.dim_cultura c USING (cultura_id)
GROUP BY s.nome_safra, c.nome_cultura
ORDER BY s.nome_safra, c.nome_cultura;
