# Modelagem analítica

## Grão das tabelas fato
- `fato_plantio`: um registro por evento/combinação de plantio.
- `fato_colheita`: um registro por evento de colheita associado a um plantio.
- `fato_aplicacao`: um registro por aplicação de insumo.
- `fato_custos`: um lançamento de custo por plantio.
- `fato_previsao`: uma previsão datada por plantio.

## Relacionamentos recomendados no Power BI
- `dim_fazenda[fazenda_id]` 1:* `dim_talhao[fazenda_id]`
- `dim_talhao[talhao_id]` 1:* `fato_plantio[talhao_id]`
- `dim_cultura[cultura_id]` 1:* `fato_plantio[cultura_id]`
- `dim_safra[safra_id]` 1:* `fato_plantio[safra_id]`
- `fato_plantio[plantio_id]` 1:* `fato_colheita[plantio_id]`
- `fato_plantio[plantio_id]` 1:* `fato_aplicacao[plantio_id]`
- `fato_plantio[plantio_id]` 1:* `fato_custos[plantio_id]`
- `fato_plantio[plantio_id]` 1:* `fato_previsao[plantio_id]`

Prefira direção de filtro única, das dimensões para os fatos. Para um modelo de produção mais rigoroso, crie dimensões de data separadas ou uma dimensão calendário com relações inativas para datas de eventos diferentes.

## Observações
- Dados inteiramente fictícios para demonstração.
- Coordenadas são pontos aproximados/ilustrativos, não limites oficiais de talhões.
- `Área Colhida` na medida DAX usa produção maior que zero como proxy. Em produção real, é melhor registrar a área efetivamente colhida em uma coluna própria.
- Não some custo total da view de plantio junto a custo de aplicações sem conferir se os dois representam despesas diferentes: aplicações podem já estar incluídas na categoria de custos de insumos.
