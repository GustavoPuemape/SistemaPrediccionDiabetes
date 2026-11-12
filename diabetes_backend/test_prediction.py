"""
Script para probar el endpoint de predicción
"""
import requests
import json

# URL del endpoint
url = "http://127.0.0.1:8000/api/predict/"

# Datos de prueba - Caso de alto riesgo
data = {
    "age": 55,
    "pulse_rate": 85,
    "systolic_bp": 150,
    "diastolic_bp": 95,
    "glucose": 220,
    "height": 165,
    "weight": 90,
    "bmi": 33.0,
    "family_diabetes": True,
    "hypertensive": True,
    "family_hypertension": True,
    "cardiovascular_disease": False,
    "stroke": False
}

print("=" * 70)
print("PRUEBA DE PREDICCIÓN - API DIABETES")
print("=" * 70)
print("\n📤 Enviando datos:")
print(json.dumps(data, indent=2))
print()

try:
    # Realizar la petición POST
    response = requests.post(url, json=data)
    
    # Verificar el código de estado
    if response.status_code == 200:
        result = response.json()
        
        print("✅ PREDICCIÓN EXITOSA")
        print("=" * 70)
        print(f"\n📊 RESULTADOS:")
        print(f"   ID de Predicción: {result['prediction_id']}")
        print(f"   Predicción: {'DIABÉTICO ⚠️' if result['result']['prediction'] else 'NO DIABÉTICO ✅'}")
        print(f"   Probabilidad: {result['result']['probability_percentage']:.2f}%")
        print(f"   Nivel de Riesgo: {result['result']['risk_level']}")
        print(f"   Umbral Usado: {result['result']['threshold']:.4f}")
        print(f"\n💬 Mensaje:")
        print(f"   {result['result']['message']}")
        print("\n" + "=" * 70)
        
    else:
        print(f"❌ Error en la petición: {response.status_code}")
        print(f"Respuesta: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: No se puede conectar al servidor")
    print("   Asegúrate de que el servidor esté corriendo:")
    print("   python manage.py runserver")
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")

print()

# Prueba 2: Caso de bajo riesgo
print("\n" + "=" * 70)
print("SEGUNDA PRUEBA - CASO DE BAJO RIESGO")
print("=" * 70)

data_low_risk = {
    "age": 30,
    "pulse_rate": 70,
    "systolic_bp": 120,
    "diastolic_bp": 80,
    "glucose": 90,
    "height": 170,
    "weight": 70,
    "bmi": 24.2,
    "family_diabetes": False,
    "hypertensive": False,
    "family_hypertension": False,
    "cardiovascular_disease": False,
    "stroke": False
}

print("\n📤 Enviando datos:")
print(json.dumps(data_low_risk, indent=2))
print()

try:
    response = requests.post(url, json=data_low_risk)
    
    if response.status_code == 200:
        result = response.json()
        
        print("✅ PREDICCIÓN EXITOSA")
        print("=" * 70)
        print(f"\n📊 RESULTADOS:")
        print(f"   ID de Predicción: {result['prediction_id']}")
        print(f"   Predicción: {'DIABÉTICO ⚠️' if result['result']['prediction'] else 'NO DIABÉTICO ✅'}")
        print(f"   Probabilidad: {result['result']['probability_percentage']:.2f}%")
        print(f"   Nivel de Riesgo: {result['result']['risk_level']}")
        print(f"\n💬 Mensaje:")
        print(f"   {result['result']['message']}")
        print("\n" + "=" * 70)
        
except Exception as e:
    print(f"❌ Error: {e}")

print()