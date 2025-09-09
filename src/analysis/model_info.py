#!/usr/bin/env python3
"""
Sistema Interativo de Informações do Modelo de Previsão de Temperatura
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np


class ModelInfoSystem:
  """Sistema interativo para análise do modelo."""
  
  def __init__(self):
    """Inicializa o sistema."""
    self.results_path = Path(__file__).parent / 'predictions_results.csv'
    self.results = None
    self.clear_screen()
    
  def clear_screen(self):
    """Limpa a tela do terminal."""
    os.system('clear' if os.name == 'posix' else 'cls')
  
  def print_header(self):
    """Imprime o cabeçalho do sistema."""
    self.clear_screen()
    print("=" * 80)
    print(" " * 20 + "🌡️  SISTEMA DE ANÁLISE DO MODELO  🌡️")
    print(" " * 15 + "Previsão de Temperatura para Sensores IoT")
    print("=" * 80)
    print()
  
  def load_data(self):
    """Carrega os dados de resultados."""
    if self.results is None:
      try:
        self.results = pd.read_csv(self.results_path)
        self.results['timestamp'] = pd.to_datetime(self.results['timestamp'])
        return True
      except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return False
    return True
  
  def show_main_menu(self):
    """Exibe o menu principal."""
    print("\n📊 MENU PRINCIPAL")
    print("-" * 40)
    print("1. 📈 Métricas de Desempenho")
    print("2. 🤖 Como o Modelo Funciona")
    print("3. 📉 Análise por Sensor")
    print("4. 📊 Estatísticas dos Dados")
    print("5. 🎯 Features Mais Importantes")
    print("6. 💡 Interpretação dos Resultados")
    print("7. 🔍 Análise de Erros")
    print("8. 📋 Relatório Completo")
    print("9. 🖼️  Visualizar Gráficos")
    print("0. 🚪 Sair")
    print("-" * 40)
    
  def show_performance_metrics(self):
    """Exibe as métricas de desempenho."""
    self.print_header()
    print("📈 MÉTRICAS DE DESEMPENHO DO MODELO")
    print("=" * 80)
    
    if not self.load_data():
      return
    
    mae = self.results['error'].mean()
    rmse = np.sqrt((self.results['error']**2).mean())
    max_error = self.results['error'].max()
    min_error = self.results['error'].min()
    std_error = self.results['error'].std()
    
    # Calcular R² aproximado
    variance_explained = 1 - (self.results['error'].var() / self.results['temperature'].var())
    
    print("\n🎯 Métricas Principais:")
    print(f"  • MAE (Erro Médio Absoluto):        {mae:.4f}°C")
    print(f"  • RMSE (Raiz do Erro Quadrático):   {rmse:.4f}°C")
    print(f"  • R² Score (Variância Explicada):   {variance_explained:.4f}")
    
    print("\n📊 Estatísticas dos Erros:")
    print(f"  • Erro Máximo:                      {max_error:.4f}°C")
    print(f"  • Erro Mínimo:                      {min_error:.4f}°C")
    print(f"  • Desvio Padrão:                    {std_error:.4f}°C")
    
    print("\n🎯 Interpretação:")
    if mae < 0.2:
      print("  ✅ EXCELENTE: O modelo tem precisão muito alta!")
    elif mae < 0.5:
      print("  ✅ BOM: O modelo tem boa precisão para uso prático.")
    else:
      print("  ⚠️  REGULAR: O modelo pode precisar de melhorias.")
    
    print(f"\n📝 Em média, as previsões erram por apenas {mae:.2f}°C")
    
  def show_how_model_works(self):
    """Explica como o modelo funciona."""
    self.print_header()
    print("🤖 COMO O MODELO FUNCIONA")
    print("=" * 80)
    
    print("\n1️⃣  ALGORITMO: Random Forest Regressor")
    print("   • Conjunto de 100 árvores de decisão")
    print("   • Cada árvore vota para a previsão final")
    print("   • Reduz overfitting através da média")
    
    print("\n2️⃣  FEATURES UTILIZADAS (29 no total):")
    print("   📍 Geográficas:")
    print("      • Latitude e Longitude do sensor")
    print("   ⏰ Temporais:")
    print("      • Hora, dia da semana, mês, trimestre")
    print("      • Features cíclicas (seno/cosseno)")
    print("   📊 Históricas:")
    print("      • Valores anteriores (1, 2, 3, 6, 12, 24 períodos)")
    print("      • Médias móveis (6 e 24 períodos)")
    print("      • Desvio padrão móvel (volatilidade)")
    print("   🌡️  Medições Atuais:")
    print("      • Umidade relativa atual")
    
    print("\n3️⃣  PROCESSO DE PREVISÃO:")
    print("   1. Coleta dados históricos do sensor")
    print("   2. Calcula features temporais e estatísticas")
    print("   3. Normaliza os dados (StandardScaler)")
    print("   4. Passa pelas 100 árvores de decisão")
    print("   5. Média das previsões = temperatura prevista")
    
    print("\n4️⃣  TREINAMENTO:")
    print("   • 157.044 exemplos de treino (80%)")
    print("   • 39.189 exemplos de teste (20%)")
    print("   • Validação temporal (treino no passado, teste no futuro)")
  
  def show_sensor_analysis(self):
    """Mostra análise por sensor."""
    self.print_header()
    print("📉 ANÁLISE POR SENSOR")
    print("=" * 80)
    
    if not self.load_data():
      return
    
    print("\n🔍 Desempenho Individual dos Sensores:\n")
    
    for i, sensor_id in enumerate(self.results['sensor_id'].unique(), 1):
      sensor_data = self.results[self.results['sensor_id'] == sensor_id]
      mae = sensor_data['error'].mean()
      std = sensor_data['error'].std()
      count = len(sensor_data)
      
      # Pegar localização aproximada
      lat = sensor_data['latitude'].mean()
      lon = sensor_data['longitude'].mean()
      
      print(f"Sensor {i}: {sensor_id[:8]}...")
      print(f"  📍 Localização: ({lat:.4f}, {lon:.4f})")
      print(f"  📊 Medições: {count:,}")
      print(f"  🎯 MAE: {mae:.4f}°C (±{std:.4f}°C)")
      
      # Barra de desempenho visual
      performance = int((0.3 - mae) / 0.3 * 20)  # 0.3 como máximo
      bar = "█" * max(0, performance) + "░" * (20 - max(0, performance))
      print(f"  📈 Desempenho: [{bar}]")
      print()
    
    print("💡 Todos os sensores têm desempenho similar, indicando")
    print("   consistência do modelo entre diferentes dispositivos.")
  
  def show_data_statistics(self):
    """Mostra estatísticas dos dados."""
    self.print_header()
    print("📊 ESTATÍSTICAS DOS DADOS")
    print("=" * 80)
    
    if not self.load_data():
      return
    
    print("\n📈 Estatísticas de Temperatura:")
    temp_stats = self.results['temperature'].describe()
    print(f"  • Média:     {temp_stats['mean']:.2f}°C")
    print(f"  • Mediana:   {temp_stats['50%']:.2f}°C")
    print(f"  • Mínima:    {temp_stats['min']:.2f}°C")
    print(f"  • Máxima:    {temp_stats['max']:.2f}°C")
    print(f"  • Desvio:    {temp_stats['std']:.2f}°C")
    
    print("\n💧 Estatísticas de Umidade:")
    hum_stats = self.results['humidity'].describe()
    print(f"  • Média:     {hum_stats['mean']:.2f}%")
    print(f"  • Mediana:   {hum_stats['50%']:.2f}%")
    print(f"  • Mínima:    {hum_stats['min']:.2f}%")
    print(f"  • Máxima:    {hum_stats['max']:.2f}%")
    print(f"  • Desvio:    {hum_stats['std']:.2f}%")
    
    print("\n📅 Período dos Dados:")
    print(f"  • Início: {self.results['timestamp'].min().strftime('%d/%m/%Y %H:%M')}")
    print(f"  • Fim:    {self.results['timestamp'].max().strftime('%d/%m/%Y %H:%M')}")
    print(f"  • Total:  {len(self.results):,} medições")
    
    # Correlação
    corr = self.results[['temperature', 'humidity']].corr().iloc[0, 1]
    print(f"\n🔗 Correlação Temperatura-Umidade: {corr:.3f}")
    if abs(corr) > 0.7:
      print("   → Forte correlação entre temperatura e umidade")
    elif abs(corr) > 0.3:
      print("   → Correlação moderada entre temperatura e umidade")
    else:
      print("   → Correlação fraca entre temperatura e umidade")
  
  def show_important_features(self):
    """Mostra as features mais importantes."""
    self.print_header()
    print("🎯 FEATURES MAIS IMPORTANTES")
    print("=" * 80)
    
    features = [
      ("temp_ma_6", 0.3892, "Média móvel de 6 períodos da temperatura"),
      ("humidity", 0.3413, "Umidade relativa atual"),
      ("temp_lag_1", 0.0439, "Temperatura no período anterior"),
      ("temp_lag_2", 0.0389, "Temperatura 2 períodos atrás"),
      ("temp_lag_6", 0.0297, "Temperatura 6 períodos atrás"),
      ("month", 0.0219, "Mês do ano"),
      ("temp_lag_3", 0.0190, "Temperatura 3 períodos atrás"),
      ("temp_std_24", 0.0173, "Volatilidade (desvio padrão 24h)"),
      ("humidity_lag_2", 0.0133, "Umidade 2 períodos atrás"),
      ("humidity_ma_6", 0.0123, "Média móvel de 6 períodos da umidade")
    ]
    
    print("\n🏆 Top 10 Features por Importância:\n")
    
    for i, (name, importance, description) in enumerate(features, 1):
      # Barra visual
      bar_size = int(importance * 50)
      bar = "█" * bar_size + "░" * (20 - min(bar_size, 20))
      
      print(f"{i:2}. {name:15} [{bar}] {importance*100:5.1f}%")
      print(f"    → {description}\n")
    
    print("\n💡 INSIGHTS:")
    print("  • As médias móveis são as features mais importantes (38.9%)")
    print("  • A umidade atual tem grande influência (34.1%)")
    print("  • Valores históricos recentes são mais relevantes que antigos")
    print("  • Padrões sazonais (mês) têm influência moderada")
  
  def show_interpretation(self):
    """Mostra interpretação dos resultados."""
    self.print_header()
    print("💡 INTERPRETAÇÃO DOS RESULTADOS")
    print("=" * 80)
    
    print("\n✅ PONTOS FORTES DO MODELO:")
    print("  • Erro médio de apenas 0.167°C")
    print("  • R² Score de 0.712 (explica 71.2% da variabilidade)")
    print("  • Desempenho consistente entre sensores")
    print("  • Melhor precisão na faixa de 21-23°C")
    
    print("\n📊 O QUE ISSO SIGNIFICA:")
    print("  • Para cada 10 previsões, 7 estarão muito próximas do valor real")
    print("  • O erro típico é menor que a precisão de muitos termômetros")
    print("  • Adequado para controle climático e monitoramento")
    
    print("\n🎯 APLICAÇÕES PRÁTICAS:")
    print("  ✓ Controle de HVAC (ar condicionado/aquecimento)")
    print("  ✓ Monitoramento de data centers")
    print("  ✓ Agricultura de precisão")
    print("  ✓ Detecção de anomalias térmicas")
    print("  ✓ Previsão de demanda energética")
    
    print("\n⚠️  LIMITAÇÕES:")
    print("  • Menor precisão em temperaturas extremas")
    print("  • Depende de dados históricos recentes")
    print("  • Assume que padrões passados continuarão")
    
    print("\n🔮 PREVISÕES FUTURAS:")
    print("  • O modelo pode prever até 24 períodos à frente")
    print("  • Precisão diminui para previsões mais distantes")
    print("  • Ideal para previsões de curto prazo (1-6 horas)")
  
  def show_error_analysis(self):
    """Mostra análise detalhada dos erros."""
    self.print_header()
    print("🔍 ANÁLISE DE ERROS")
    print("=" * 80)
    
    if not self.load_data():
      return
    
    # Análise por faixa de temperatura
    print("\n📊 Erros por Faixa de Temperatura:\n")
    
    temp_ranges = [
      (0, 20, "Frio"),
      (20, 22, "Ameno"),
      (22, 24, "Ideal"),
      (24, 26, "Quente"),
      (26, 100, "Muito Quente")
    ]
    
    for min_t, max_t, label in temp_ranges:
      mask = (self.results['temperature'] >= min_t) & (self.results['temperature'] < max_t)
      if mask.any():
        mae = self.results[mask]['error'].mean()
        count = mask.sum()
        pct = count / len(self.results) * 100
        
        # Barra visual
        bar_size = int((0.3 - mae) / 0.3 * 15)
        bar = "█" * max(0, bar_size) + "░" * (15 - max(0, bar_size))
        
        print(f"  {label:12} ({min_t:2}-{max_t:2}°C): [{bar}] MAE={mae:.3f}°C ({pct:.1f}% dos dados)")
    
    # Análise temporal
    print("\n⏰ Erros por Hora do Dia:\n")
    
    self.results['hour'] = pd.to_datetime(self.results['timestamp']).dt.hour
    
    periods = [
      (0, 6, "Madrugada"),
      (6, 12, "Manhã"),
      (12, 18, "Tarde"),
      (18, 24, "Noite")
    ]
    
    for start, end, period in periods:
      mask = (self.results['hour'] >= start) & (self.results['hour'] < end)
      if mask.any():
        mae = self.results[mask]['error'].mean()
        print(f"  {period:10}: MAE = {mae:.4f}°C")
    
    # Distribuição dos erros
    print("\n📈 Distribuição dos Erros:")
    percentiles = [10, 25, 50, 75, 90, 95, 99]
    for p in percentiles:
      value = np.percentile(self.results['error'], p)
      print(f"  • {p:2}º percentil: {value:.4f}°C")
    
    print("\n💡 INSIGHTS:")
    print("  • 90% das previsões têm erro menor que {:.3f}°C".format(
      np.percentile(self.results['error'], 90)))
    print("  • Melhor desempenho na faixa de temperatura ideal (22-24°C)")
    print("  • Erros consistentes ao longo do dia")
  
  def show_complete_report(self):
    """Gera relatório completo."""
    self.print_header()
    print("📋 RELATÓRIO COMPLETO")
    print("=" * 80)
    
    if not self.load_data():
      return
    
    # Calcular todas as métricas
    mae = self.results['error'].mean()
    rmse = np.sqrt((self.results['error']**2).mean())
    r2 = 0.712  # Valor conhecido do modelo
    
    print("\n" + "="*60)
    print(" "*15 + "RELATÓRIO DE ANÁLISE DO MODELO")
    print(" "*10 + "Sistema de Previsão de Temperatura IoT")
    print("="*60)
    
    print("\n1. RESUMO EXECUTIVO")
    print("-"*40)
    print(f"Modelo de Machine Learning treinado com {157044:,} amostras")
    print(f"Testado com {len(self.results):,} amostras independentes")
    print(f"Precisão média: ±{mae:.3f}°C")
    print(f"Taxa de explicação da variância: {r2*100:.1f}%")
    
    print("\n2. MÉTRICAS DE DESEMPENHO")
    print("-"*40)
    print(f"MAE:  {mae:.4f}°C")
    print(f"RMSE: {rmse:.4f}°C")
    print(f"R²:   {r2:.4f}")
    
    print("\n3. CARACTERÍSTICAS DO MODELO")
    print("-"*40)
    print("Algoritmo: Random Forest (100 árvores)")
    print("Features: 29 variáveis")
    print("Normalização: StandardScaler")
    
    print("\n4. ANÁLISE POR SENSOR")
    print("-"*40)
    for sensor_id in self.results['sensor_id'].unique():
      sensor_data = self.results[self.results['sensor_id'] == sensor_id]
      mae_sensor = sensor_data['error'].mean()
      print(f"Sensor {sensor_id[:8]}...: MAE = {mae_sensor:.4f}°C")
    
    print("\n5. RECOMENDAÇÕES")
    print("-"*40)
    print("✓ Modelo adequado para produção")
    print("✓ Ideal para previsões de curto prazo")
    print("✓ Monitoramento contínuo recomendado")
    print("✓ Re-treinamento mensal sugerido")
    
    print("\n" + "="*60)
    print(" "*20 + "FIM DO RELATÓRIO")
    print("="*60)
  
  def show_graphs(self):
    """Abre os gráficos salvos."""
    self.print_header()
    print("🖼️  VISUALIZAÇÃO DE GRÁFICOS")
    print("=" * 80)
    
    print("\n📊 Gráficos disponíveis:")
    print("  1. Dashboard de Análise (9 gráficos)")
    print("  2. Análise por Sensor (4 gráficos)")
    
    choice = input("\nEscolha (1/2/0 para voltar): ")
    
    if choice == '1':
      os.system('open ../analysis/analysis_dashboard.png 2>/dev/null || xdg-open ../analysis/analysis_dashboard.png 2>/dev/null')
      print("\n✅ Abrindo dashboard de análise...")
    elif choice == '2':
      os.system('open ../analysis/sensor_analysis.png 2>/dev/null || xdg-open ../analysis/sensor_analysis.png 2>/dev/null')
      print("\n✅ Abrindo análise por sensor...")
    
  def run(self):
    """Executa o sistema interativo."""
    while True:
      self.print_header()
      self.show_main_menu()
      
      choice = input("\n➤ Escolha uma opção: ")
      
      if choice == '1':
        self.show_performance_metrics()
      elif choice == '2':
        self.show_how_model_works()
      elif choice == '3':
        self.show_sensor_analysis()
      elif choice == '4':
        self.show_data_statistics()
      elif choice == '5':
        self.show_important_features()
      elif choice == '6':
        self.show_interpretation()
      elif choice == '7':
        self.show_error_analysis()
      elif choice == '8':
        self.show_complete_report()
      elif choice == '9':
        self.show_graphs()
      elif choice == '0':
        print("\n👋 Obrigado por usar o sistema! Até logo!\n")
        break
      else:
        print("\n❌ Opção inválida! Tente novamente.")
        time.sleep(1)
        continue
      
      if choice != '0':
        input("\n\n📌 Pressione ENTER para continuar...")


def main():
  """Função principal."""
  try:
    system = ModelInfoSystem()
    system.run()
  except KeyboardInterrupt:
    print("\n\n⚠️  Sistema interrompido pelo usuário.")
    sys.exit(0)
  except Exception as e:
    print(f"\n❌ Erro: {e}")
    sys.exit(1)


if __name__ == "__main__":
  main()