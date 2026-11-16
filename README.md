# Automação do Cálculo do Índice de Suscetibilidade em Python (ArcPy)

Script desenvolvido em **Python (`ArcPy`)** para automatizar o cálculo espacial do **Índice de Suscetibilidade** (com e sem a componente de Uso e Ocupação do Solo), integrando projeção automática de dados, análise de terreno, conversão vetorial-matricial e álgebra de mapas.

* **Contexto:** Mestrado em Sistemas de Informação Geográfica e Ordenamento do Território — Introdução à Programação em SIG (FLUP)
* **Autores:** Luís Costa e Diogo Nogueira | **Docentes:** Prof. António Coelho e Prof. Ricardo Baptista
* **Tecnologias:** Python 2.7, ArcPy (Spatial Analyst & 3D Analyst), ArcGIS Desktop 10.x
* **Sistema de Coordenadas:** `ETRS_1989_Portugal_TM06` (`EPSG:3763`)

---

## 🎯 Funcionalidades do Script

1. **Gestão de Ambiente e Projeções:**
   * Definição automática de resolução espacial (`cellSize = 5m`) e sistema de coordenadas (`EPSG:3763`).
   * Iteração sobre *shapefiles* e *rasters* da pasta de entrada para verificação e reprojeção (`DefineProjection` e `Project`).
2. **Derivação de Parâmetros Biofísicos:**
   * **Parâmetro `T` (Declives):** Cálculo de declives em percentagem a partir do MDE (`Slope_3d`) e reclassificação segundo as normas da RCM.
   * **Parâmetros Geológicos (`D`, `R`, `A`):** Conversão automática de atributos vetoriais para formato matricial (`FeatureToRaster`).
   * **Parâmetro `LU` (Uso do Solo):** Conversão vetorial-matricial da carta de ocupação do solo (`PolygonToRaster`).
3. **Álgebra de Mapas e Classificação Final:**
   * Cálculo ponderado de dois cenários distintos (**Índice 1** sem uso do solo e **Índice 2** com uso do solo).
   * Reclassificação automática dos mapas finais em classes de suscetibilidade.

---

## 📊 Modelos e Ponderações Aplicadas

### Modelo 1: Índice de Suscetibilidade (DRAT — sem Uso do Solo)
Baseado nos pesos definidos por Veríssimo (2010):

| Parâmetro | Descrição | Peso |
| :--- | :--- | :---: |
| **D** | Litologia / Geologia (D) | **0.24** |
| **R** | Estrutura / Geologia (R) | **0.33** |
| **A** | Alteração / Geologia (A) | **0.27** |
| **T** | Declives (%) | **0.16** |

### Modelo 2: Índice de Suscetibilidade (DRAT + LU — com Uso do Solo)
Baseado nos pesos definidos por Ribeiro (2005b):

| Parâmetro | Descrição | Peso |
| :--- | :--- | :---: |
| **D** | Litologia / Geologia (D) | **0.186** |
| **R** | Estrutura / Geologia (R) | **0.212** |
| **A** | Alteração / Geologia (A) | **0.259** |
| **T** | Declives (%) | **0.121** |
| **LU** | Uso e Ocupação do Solo | **0.222** |

---

## 🗺️ Resultados Gerados
![Comparação dos Índices de Suscetibilidade](imagens/resultados-indices.png)
*(À esquerda: Índice sem Uso do Solo | À direita: Índice com Uso do Solo)*

---

## 📂 Estrutura do Repositório
* 🐍 **[Scripts Python (`src/`)](src/)** — Código-fonte em `ArcPy` para execução direta e versão experimental parametrizada com `arcpy.GetParameterAsText()` para integração em *ArcToolbox* (`.tbx`).
* 📄 **[Relatório Técnico (PDF)](docs/relatorio-indice-suscetibilidade-arcpy.pdf)** — Documentação completa da arquitetura do código, excertos comentados e notas sobre a criação da *Toolbox*.