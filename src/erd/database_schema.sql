-- Esquema de Banco de Dados de Sensores
-- Script de criação das tabelas

-- Tabela SENSOR
CREATE TABLE SENSOR (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  sensor_uuid UUID UNIQUE NOT NULL,
  sensor_name VARCHAR(255),
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE
);

-- Tabela SENSOR_TYPE
CREATE TABLE SENSOR_TYPE (
  id INT PRIMARY KEY AUTO_INCREMENT,
  type_name VARCHAR(100) NOT NULL,
  manufacturer VARCHAR(255),
  model VARCHAR(255),
  humidity_min_range DECIMAL(5, 2),
  humidity_max_range DECIMAL(5, 2),
  temp_min_range DECIMAL(5, 2),
  temp_max_range DECIMAL(5, 2),
  accuracy DECIMAL(5, 4)
);

-- Adicionar coluna type_id na tabela SENSOR para relacionamento com SENSOR_TYPE
ALTER TABLE SENSOR ADD COLUMN type_id INT;
ALTER TABLE SENSOR ADD CONSTRAINT fk_sensor_type 
  FOREIGN KEY (type_id) REFERENCES SENSOR_TYPE(id);

-- Tabela MEASUREMENT
CREATE TABLE MEASUREMENT (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  sensor_id BIGINT NOT NULL,
  humidity DECIMAL(5, 2) CHECK (humidity >= 0 AND humidity <= 100),
  temperature DECIMAL(5, 2),
  timestamp TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (sensor_id) REFERENCES SENSOR(id)
);

-- Tabela ALERT_RULE
CREATE TABLE ALERT_RULE (
  id INT PRIMARY KEY AUTO_INCREMENT,
  sensor_id BIGINT NOT NULL,
  rule_name VARCHAR(255) NOT NULL,
  condition_type VARCHAR(50) CHECK (condition_type IN ('>', '<', 'BETWEEN')),
  threshold_min DECIMAL(10, 2),
  threshold_max DECIMAL(10, 2),
  metric_type VARCHAR(50) CHECK (metric_type IN ('humidity', 'temperature')),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (sensor_id) REFERENCES SENSOR(id)
);

-- Tabela ALERT_LOG
CREATE TABLE ALERT_LOG (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  rule_id INT NOT NULL,
  measurement_id BIGINT NOT NULL,
  alert_level VARCHAR(50) CHECK (alert_level IN ('WARNING', 'CRITICAL')),
  message TEXT,
  triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_resolved BOOLEAN DEFAULT FALSE,
  resolved_at TIMESTAMP NULL,
  FOREIGN KEY (rule_id) REFERENCES ALERT_RULE(id),
  FOREIGN KEY (measurement_id) REFERENCES MEASUREMENT(id)
);
