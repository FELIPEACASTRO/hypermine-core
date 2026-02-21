# Projeção Financeira Detalhada — 1 Ano de Mineração

**Fonte:** Google Gemini 2.5 Flash
**Data:** Fevereiro 2026

---

## Projeção de Lucro Detalhada para Mineração (1 Ano) - Notebook Acer Nitro 5

**Analista Financeiro Especializado em Mineração de Criptomoedas**

**Data da Análise:** Fevereiro de 2024
**Período da Projeção:** 1 ano (365 dias), com início em Fevereiro de 2026 (baseado nos preços fornecidos)

### 1. Introdução

Esta análise detalhada projeta a rentabilidade da mineração de criptomoedas por um período de 12 meses (365 dias) utilizando um notebook Acer Nitro 5 com as especificações fornecidas. Serão considerados diversos fatores, como custos de energia no Brasil, flutuações de dificuldade, degradação de hardware e otimização através de *profit-switching*. A projeção será apresentada em cenários realista, otimista e pessimista, utilizando os preços de criptomoedas fornecidos como base para "fevereiro de 2026".

### 2. Premissas e Dados Iniciais

Para a elaboração desta projeção, as seguintes premissas e dados foram utilizados:

*   **Hardware:** Notebook Acer Nitro 5 (CPU: i5-9300H, GPU: GTX 1650 4GB, RAM: 16GB).
*   **Consumo Total do Sistema:**
    *   Mineração via GPU: ~120W (0.12 kWh)
    *   Mineração via CPU (XMR): ~75W (0.075 kWh - estimado como 45W CPU + 30W sistema base)
*   **Custo de Energia (Brasil):** R$0.88/kWh (equivalente a ~$0.176/kWh, considerando 1 USD = R$5.00).
*   **Taxa de Câmbio:** 1 USD = R$5.00 (para fins de projeção).
*   **Período de Análise:** 12 meses (Fevereiro 2026 a Janeiro 2027).
*   **Preços das Criptomoedas (Fevereiro 2026 - *Valores hipotéticos fornecidos para a análise*):**
    *   ETC: ~$18
    *   ERG: ~$0.30
    *   RVN: ~$0.006
    *   KAS: ~$0.031
    *   ALPH: ~$0.50
    *   CFX: ~$0.08
    *   XMR: ~$230
*   **Variação da Dificuldade:** Aumento médio de 5% ao mês. Este aumento reduz a quantidade de moedas mineradas para o mesmo hashrate.
*   **Degradação do Hardware:** Redução de 2% no hashrate efetivo após 6 meses (aplicado a partir do 7º mês).
*   **Custo de Manutenção:** R$33.33/mês (equivalente a ~$6.67/mês), cobrindo custos como pasta térmica e um *cooling pad* ao longo do ano.
*   **Profit-Switching com ML:** Ganho estimado de 20% sobre a receita bruta da mineração de uma única moeda (utilizando o ponto médio do intervalo de 15-25% fornecido). Este ganho é aplicado sobre a moeda mais rentável identificada.
*   **Cenários de Preço:**
    *   **Realista:** Preços estáveis (conforme os valores fornecidos).
    *   **Otimista:** Preços sobem 50% em relação aos valores fornecidos.
    *   **Pessimista:** Preços caem 30% em relação aos valores fornecidos.

### 3. Seleção da Moeda Mais Rentável (Base)

Com base nos hashrates e preços fornecidos, e considerando a eficiência da GPU GTX 1650, calculamos a rentabilidade diária aproximada para cada moeda antes dos custos de energia e profit-switching:

*   **ETC (Etchash):** 18 MH/s @ $18/ETC -> ~$0.162/dia
*   **RVN (KAWPOW):** 8.1 MH/s @ $0.006/RVN -> ~$0.162/dia
*   **ERG (Autolykos2):** 36 MH/s @ $0.30/ERG -> ~$0.150/dia
*   **KAS (kHeavyHash):** 200 MH/s @ $0.031/KAS -> **~$0.310/dia (Estimativa de 10 KAS/dia)**
*   **ALPH (Blake3):** 450 MH/s @ $0.50/ALPH -> ~$0.250/dia
*   **CFX (Octopus):** 8.9 MH/s @ $0.08/CFX -> ~$0.200/dia
*   **XMR (RandomX - CPU):** 2.5 kH/s @ $230/XMR (considerando 75W de consumo total) -> ~$0.009/dia (muito baixo)

A moeda **KASPA (KAS)** apresenta a maior rentabilidade bruta diária com base nos dados fornecidos e será utilizada como referência para a base de cálculo da mineração por profit-switching.

**Cálculo da Receita Bruta Base Mensal (KASPA):**
*   Receita diária base (KAS): $0.310 USD
*   Receita mensal base (KAS): $0.310 USD/dia * 30.4167 dias/mês = $9.429 USD/mês

### 4. Custos Fixos Mensais

*   **Custo de Energia (GPU Mining - 120W):**
    *   0.12 kWh * 24 horas/dia * 30.4167 dias/mês = 87.59 kWh/mês
    *   Custo em BRL: 87.59 kWh/mês * R$0.88/kWh = R$77.08/mês
    *   Custo em USD: R$77.08 / 5.00 = $15.42/mês
*   **Custo de Manutenção:**
    *   Custo em BRL: R$33.33/mês
    *   Custo em USD: R$33.33 / 5.00 = $6.67/mês

**Custo Total Fixo Mensal (Energia + Manutenção):**
*   USD: $15.42 + $6.67 = $22.09/mês
*   BRL: R$77.08 + R$33.33 = R$110.41/mês

### 5. Projeção de Lucro Detalhada (12 Meses)

A tabela abaixo detalha a projeção de lucro para cada cenário, considerando os ajustes mensais de dificuldade, degradação do hardware e o ganho do *profit-switching*.

**Fatores de Ajuste Mensais:**

*   **Dificuldade:** (1 - 0.05)^(Mês-1)
*   **Degradação:** Multiplicador de 0.98 a partir do Mês 7.
*   **Profit-Switching:** Multiplicador de 1.20 na receita bruta base.

| Mês | Fator Dificuldade | Fator Degrad. | Fator Total Efetivo | Receita Bruta Base Mensal (USD) | Receita Bruta c/ Profit-Switch (USD) |
| :-- | :---------------- | :------------ | :------------------ | :------------------------------ | :----------------------------------- |
| 1   | 1.000             | 1.00          | 1.000               | $9.43                           | $11.31                               |
| 2   | 0.950             | 1.00          | 0.950               | $8.96                           | $10.75                               |
| 3   | 0.902             | 1.00          | 0.902               | $8.51                           | $10.21                               |
| 4   | 0.857             | 1.00          | 0.857               | $8.08                           | $9.70                                |
| 5   | 0.815             | 1.00          | 0.815               | $7.68                           | $9.21                                |
| 6   | 0.774             | 1.00          | 0.774               | $7.30                           | $8.76                                |
| 7   | 0.735             | 0.98          | 0.720               | $6.80                           | $8.16                                |
| 8   | 0.698             | 0.98          | 0.684               | $6.45                           | $7.74                                |
| 9   | 0.663             | 0.98          | 0.650               | $6.13                           | $7.36                                |
| 10  | 0.630             | 0.98          | 0.618               | $5.82                           | $6.98                                |
| 11  | 0.599             | 0.98          | 0.587               | $5.53                           | $6.64                                |
| 12  | 0.569             | 0.98          | 0.558               | $5.26                           | $6.31                                |

---

**Tabela de Projeção Mensal de Lucro Líquido (USD e BRL)**

| Mês | **Receita Bruta (USD)** | **Receita Bruta (BRL)** | **Custo Energia (USD)** | **Custo Energia (BRL)** | **Custo Manut. (USD)** | **Custo Manut. (BRL)** | **Lucro Líquido (USD)** | **Lucro Líquido (BRL)** |
| :-- | :---------------------- | :---------------------- | :---------------------- | :---------------------- | :--------------------- | :--------------------- | :---------------------- | :---------------------- |
| **Cenário Realista (Preços Estáveis)** | | | | | | | | |
| 1   | $11.31                  | R$56.55                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$10.78**             | **-R$53.86**            |
| 2   | $10.75                  | R$53.75                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$11.34**             | **-R$56.66**            |
| 3   | $10.21                  | R$51.05                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$11.88**             | **-R$59.41**            |
| 4   | $9.70                   | R$48.50                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$12.39**             | **-R$61.91**            |
| 5   | $9.21                   | R$46.05                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$12.88**             | **-R$64.41**            |
| 6   | $8.76                   | R$43.80                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$13.33**             | **-R$66.61**            |
| 7   | $8.16                   | R$40.80                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$13.93**             | **-R$69.61**            |
| 8   | $7.74                   | R$38.70                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$14.35**             | **-R$71.71**            |
| 9   | $7.36                   | R$36.80                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$14.73**             | **-R$73.61**            |
| 10  | $6.98                   | R$34.90                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$15.11**             | **-R$75.51**            |
| 11  | $6.64                   | R$33.20                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$15.45**             | **-R$77.21**            |
| 12  | $6.31                   | R$31.55                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$15.78**             | **-R$78.91**            |
| **Total Anual** | **$107.44**             | **R$537.20**            | **$185.04**             | **R$924.96**            | **$80.04**             | **R$400.00**           | **-$157.64**            | **-R$787.76**           |
| | | | | | | | | |
| **Cenário Otimista (Preços +50%)** | | | | | | | | |
| 1   | $16.97                  | R$84.85                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$5.12**              | **-R$25.56**            |
| 2   | $16.13                  | R$80.65                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$5.96**              | **-R$29.81**            |
| 3   | $15.32                  | R$76.60                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$6.77**              | **-R$33.81**            |
| 4   | $14.55                  | R$72.75                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$7.54**              | **-R$37.71**            |
| 5   | $13.82                  | R$69.10                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$8.27**              | **-R$41.36**            |
| 6   | $13.14                  | R$65.70                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$8.95**              | **-R$44.76**            |
| 7   | $12.24                  | R$61.20                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$9.85**              | **-R$49.21**            |
| 8   | $11.61                  | R$58.05                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$10.48**             | **-R$52.41**            |
| 9   | $11.04                  | R$55.20                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$11.05**             | **-R$55.26**            |
| 10  | $10.47                  | R$52.35                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$11.62**             | **-R$58.11**            |
| 11  | $9.96                   | R$49.80                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$12.13**             | **-R$60.61**            |
| 12  | $9.47                   | R$47.35                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$12.62**             | **-R$63.11**            |
| **Total Anual** | **$160.72**             | **R$803.60**            | **$185.04**             | **R$924.96**            | **$80.04**             | **R$400.00**           | **-$104.36**            | **-R$521.40**           |
| | | | | | | | | |
| **Cenário Pessimista (Preços -30%)** | | | | | | | | |
| 1   | $7.92                   | R$39.60                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$14.17**             | **-R$70.81**            |
| 2   | $7.53                   | R$37.65                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$14.56**             | **-R$72.81**            |
| 3   | $7.15                   | R$35.75                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$14.94**             | **-R$74.71**            |
| 4   | $6.80                   | R$34.00                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$15.29**             | **-R$76.41**            |
| 5   | $6.45                   | R$32.25                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$15.64**             | **-R$78.11**            |
| 6   | $6.13                   | R$30.65                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$15.96**             | **-R$79.81**            |
| 7   | $5.71                   | R$28.55                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$16.38**             | **-R$81.86**            |
| 8   | $5.42                   | R$27.10                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$16.67**             | **-R$83.31**            |
| 9   | $5.15                   | R$25.75                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$16.94**             | **-R$84.66**            |
| 10  | $4.89                   | R$24.45                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$17.20**             | **-R$85.91**            |
| 11  | $4.65                   | R$23.25                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$17.44**             | **-R$87.11**            |
| 12  | $4.42                   | R$22.10                 | $15.42                  | R$77.08                 | $6.67                  | R$33.33                | **-$17.67**             | **-R$88.31**            |
| **Total Anual** | **$75.14**              | **R$375.90**            | **$185.04**             | **R$924.96**            | **$80.04**             | **R$400.00**           | **-$189.94**            | **-R$949.06**           |

### 6. Análise dos Resultados

Os resultados da projeção indicam que a mineração com o notebook Acer Nitro 5, mesmo com a otimização de *profit-switching* e os preços de criptomoedas hipotéticos de Fevereiro de 2026, apresenta desafios significativos de rentabilidade, principalmente devido ao alto custo da energia no Brasil e à ineficiência inerente de um notebook para mineração contínua.

*   **Cenário Realista:** Em um cenário de preços estáveis, o lucro líquido mensal é consistentemente negativo, com uma perda anual acumulada de **-$157.64 USD (-R$787.76)**. A receita gerada não é suficiente para cobrir os custos fixos de energia e manutenção, que juntos somam $22.09 USD (R$110.41) por mês. A tendência é de piora gradual ao longo do ano devido ao aumento da dificuldade e degradação do hardware.
*   **Cenário Otimista:** Mesmo com um aumento de 50% nos preços das criptomoedas, a situação melhora, mas o lucro líquido ainda permanece negativo ao longo de todo o ano, com uma perda anual de **-$104.36 USD (-R$521.40)**. Isso sublinha a grande barreira que o custo de energia representa para operações de mineração de pequena escala e baixa eficiência no Brasil.
*   **Cenário Pessimista:** Com uma queda de 30% nos preços, as perdas se acentuam significativamente, resultando em um prejuízo anual de **-$189.94 USD (-R$949.06)**.

**Conclusões Adicionais:**

*   **Eficiência do Hardware:** Notebooks, embora possam minerar, não são otimizados para esta atividade. Seu sistema de resfriamento é dimensionado para uso intermitente, não para carga contínua 24/7, o que pode levar a superaquecimento, throttling (redução de desempenho) e desgaste prematuro dos componentes, além de ter uma relação hashrate/watt inferior a equipamentos dedicados (ASICs ou GPUs de desktop em rigs otimizadas).
*   **Custo de Energia no Brasil:** A tarifa de R$0.88/kWh é um dos principais fatores que inviabilizam a rentabilidade neste cenário. Para se tornar lucrativo, seria necessário um preço de criptomoeda muito mais elevado, um hashrate significativamente maior com o mesmo consumo, ou uma redução drástica no custo da energia.
*   **Profit-Switching:** Embora o *profit-switching* melhore a receita bruta em 20%, ele não é suficiente para superar o déficit gerado pelos altos custos e baixa eficiência.
*   **Desgaste e Manutenção:** Os custos de manutenção, embora pequenos, somam-se aos prejuízos. O risco de danos permanentes ao hardware (e a consequente perda do valor do notebook) por mineração contínua é alto e não foi monetizado nesta projeção, mas é um fator crítico a ser considerado.

### 7. Recomendações

Com base nesta análise, a mineração de criptomoedas com um notebook Acer Nitro 5 nas condições atuais e projetadas (preços de Fevereiro de 2026 e custo de energia no Brasil) é **altamente desaconselhada do ponto de vista financeiro**, pois consistentemente gera prejuízo líquido.

Caso a mineração ainda seja considerada, alternativas seriam:
1.  **Acesso a energia de custo muito inferior:** Em locais com energia subsidiada ou extremamente barata (idealmente abaixo de $0.05/kWh).
2.  **Hardware mais eficiente:** Investir em hardware dedicado (ASICs para KASPA, por exemplo, se houver um disponível para o algoritmo kHeavyHash, ou rigs de mineração com GPUs de desktop de alta eficiência) que ofereça uma relação hashrate/watt muito superior.
3.  **Aumento substancial nos preços das criptomoedas:** Uma valorização extraordinária e sustentada dos ativos digitais que supere amplamente o aumento da dificuldade.

Em resumo, a operação de mineração com este hardware e estrutura de custos não é viável para gerar lucro líquido ao longo do período de um ano.