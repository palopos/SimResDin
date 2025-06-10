# 🚀 Simulador de Respuesta Dinámica (Sistemas 1° y 2° Orden)


Herramienta interactiva para análisis de sistemas dinámicos, desarrollada para la asignatura **Regulación Automática** de la Universidad de Cádiz.

## 📌 Características Clave
- **Simulación en tiempo real** de sistemas:
  - Primer orden: Parámetros `k` (ganancia) y `τ` (constante de tiempo)
  - Segundo orden: Parámetros `ωₙ` (frecuencia natural) y `ζ` (amortiguamiento)
- **Entradas soportadas**:
  - Escalón unitario
  - Impulso
- **Visualización profesional**:
  - Gráficos con anotaciones de parámetros clave (*overshoot*, tiempo de establecimiento, etc.)
  - Comparación entrada/salida
- **Cálculo automático** de métricas:
  - Tiempo de subida (*rise time*)
  - Sobreimpulso (*overshoot*)
  - Tiempo de establecimiento (*settling time*)

## 🛠️ Instalación Local

### Requisitos Previos
- Python 3.8 o superior
- Gestor de paquetes `pip`

### Pasos:
1. Clonar el repositorio:
   git clone https://github.com/palopos/SimResDin.git
   cd SimResDin

2. Instalar dependencias:
    pip install -r requirements.txt

3. Ejecutar la aplicación:
    streamlit run SimResDin.py
