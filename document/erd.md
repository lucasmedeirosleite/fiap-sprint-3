# Esquema de Banco de Dados de Sensores

## Diagrama Entidade-Relacionamento

```mermaid
erDiagram
    SENSOR {
        bigint id PK "Primary Key - Auto Increment"
        uuid sensor_uuid UK "Unique Key - UUID from CSV"
        varchar sensor_name "Sensor Name/Description"
        decimal latitude "Latitude Coordinate"
        decimal longitude "Longitude Coordinate"
        datetime created_at "Installation Date"
        boolean is_active "Sensor Status"
    }
    
    MEASUREMENT {
        bigint id PK "Primary Key - Auto Increment"
        bigint sensor_id FK "Foreign Key to SENSOR"
        decimal humidity "Relative Humidity (%)"
        decimal temperature "Temperature (Celsius)"
        datetime timestamp "Measurement Timestamp"
        datetime created_at "Record Creation Date"
    }
    
    SENSOR_TYPE {
        int id PK "Primary Key"
        varchar type_name "Sensor Type Name"
        varchar manufacturer "Manufacturer Name"
        varchar model "Model Number"
        decimal humidity_min_range "Min Humidity Range (%)"
        decimal humidity_max_range "Max Humidity Range (%)"
        decimal temp_min_range "Min Temperature Range (°C)"
        decimal temp_max_range "Max Temperature Range (°C)"
        decimal accuracy "Measurement Accuracy"
    }
    
    ALERT_RULE {
        int id PK "Primary Key"
        bigint sensor_id FK "Foreign Key to SENSOR"
        varchar rule_name "Alert Rule Name"
        varchar condition_type "Condition Type (>, <, BETWEEN)"
        decimal threshold_min "Minimum Threshold Value"
        decimal threshold_max "Maximum Threshold Value"
        varchar metric_type "Metric (humidity/temperature)"
        boolean is_active "Rule Status"
        datetime created_at "Rule Creation Date"
    }
    
    ALERT_LOG {
        bigint id PK "Primary Key"
        int rule_id FK "Foreign Key to ALERT_RULE"
        bigint measurement_id FK "Foreign Key to MEASUREMENT"
        varchar alert_level "Alert Level (WARNING/CRITICAL)"
        varchar message "Alert Message"
        datetime triggered_at "Alert Trigger Time"
        boolean is_resolved "Resolution Status"
        datetime resolved_at "Resolution Time"
    }

    SENSOR ||--o{ MEASUREMENT : "generates"
    SENSOR ||--|| SENSOR_TYPE : "has_type"
    SENSOR ||--o{ ALERT_RULE : "monitors"
    ALERT_RULE ||--o{ ALERT_LOG : "triggers"
    MEASUREMENT ||--o{ ALERT_LOG : "evaluated_in"
```

## Descrição das Tabelas do Banco de Dados

### SENSOR
Armazena informações sobre cada dispositivo sensor físico.
- **id**: Chave primária bigint auto-incremento
- **sensor_uuid**: Identificador UUID correspondente à coluna sensor_id do CSV (restrição única)
- **sensor_name**: Nome legível do sensor
- **latitude**: Coordenada de latitude da localização do sensor (graus decimais)
- **longitude**: Coordenada de longitude da localização do sensor (graus decimais)
- **created_at**: Quando o sensor foi registrado pela primeira vez
- **is_active**: Se o sensor está atualmente operacional

### MEASUREMENT
Armazena leituras individuais dos sensores (corresponde às linhas do CSV).
- **id**: Chave primária auto-incremento
- **sensor_id**: Ligação com a tabela SENSOR
- **humidity**: Porcentagem de umidade relativa (0-100%)
- **temperature**: Temperatura em Celsius
- **timestamp**: Quando a medição foi realizada
- **created_at**: Quando o registro foi inserido no banco de dados

### SENSOR_TYPE
Define diferentes tipos/modelos de sensores com suas especificações.
- **id**: Chave primária para tipos de sensor
- **type_name**: Nome descritivo (ex: "DHT22", "BME280")
- **manufacturer**: Fabricante do sensor
- **model**: Número do modelo
- **humidity_min_range/humidity_max_range**: Faixa operacional de umidade (%)
- **temp_min_range/temp_max_range**: Faixa operacional de temperatura (°C)
- **accuracy**: Especificação de precisão da medição

### ALERT_RULE
Regras configuráveis para monitoramento de valores dos sensores.
- **id**: Chave primária para regras de alerta
- **sensor_id**: Para qual sensor esta regra se aplica
- **rule_name**: Nome descritivo para a regra
- **condition_type**: Tipo de condição (maior que, menor que, entre)
- **threshold_min/threshold_max**: Valores de limite para alertas
- **metric_type**: Se a regra se aplica a umidade ou temperatura
- **is_active**: Se a regra está atualmente habilitada

### ALERT_LOG
Registro histórico de alertas disparados.
- **id**: Chave primária para eventos de alerta
- **rule_id**: Qual regra disparou este alerta (referência para ALERT_RULE.id)
- **measurement_id**: A medição que disparou o alerta (referência para MEASUREMENT.id)
- **alert_level**: Nível de severidade do alerta
- **message**: Mensagem de alerta legível
- **triggered_at**: Quando o alerta foi disparado
- **is_resolved**: Se a condição do alerta foi resolvida
- **resolved_at**: Quando o alerta foi marcado como resolvido

## Relacionamentos Principais

1. **Um-para-Muitos**: Cada sensor pode gerar múltiplas medições
2. **Um-para-Um**: Cada sensor tem um tipo de sensor
3. **Um-para-Muitos**: Cada sensor pode ter múltiplas regras de alerta
4. **Um-para-Muitos**: Cada regra de alerta pode disparar múltiplos alertas
5. **Um-para-Muitos**: Cada medição pode ser avaliada em múltiplos alertas

## Tipos de Dados e Restrições

- **UUIDs**: Usados para identificação de sensores para corresponder ao formato CSV
- **Decimal**: Usado para valores de medição precisos (umidade %, temperatura °C)
- **DateTime**: Todos os timestamps com suporte a fuso horário
- **Restrições**: 
  - Valores de umidade: 0-100%
  - Valores de temperatura: Faixas razoáveis (-40°C a 85°C para sensores típicos)
  - Restrições de chave estrangeira garantem integridade dos dados