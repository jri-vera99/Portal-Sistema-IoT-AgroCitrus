from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import logging
from emergentintegrations.llm.chat import LlmChat, UserMessage
from config import EMERGENT_LLM_KEY
from influx_client import influx_manager
import json

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        self.api_key = EMERGENT_LLM_KEY
        self.model = "gpt-4o-mini"
        self.provider = "openai"
    
    async def analyze_sensor_data(self, analysis_type: str = "general", 
                                  time_range_hours: int = 24,
                                  node_id: str = None) -> Dict[str, Any]:
        """Analyze sensor data using AI"""
        try:
            # Get historical data
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=time_range_hours)
            
            # Query data for different sensor types
            temperature_data = influx_manager.query_historical_data(
                "temperature", start_time, end_time, node_id, "mean", "15m"
            )
            humidity_data = influx_manager.query_historical_data(
                "air_humidity", start_time, end_time, node_id, "mean", "15m"
            )
            soil_moisture_data = influx_manager.query_historical_data(
                "soil_moisture", start_time, end_time, node_id, "mean", "15m"
            )
            luminosity_data = influx_manager.query_historical_data(
                "luminosity", start_time, end_time, node_id, "mean", "15m"
            )
            
            # Prepare data summary for AI
            data_summary = self._prepare_data_summary(
                temperature_data, humidity_data, soil_moisture_data, luminosity_data
            )
            
            # Create AI prompt
            prompt = self._create_analysis_prompt(analysis_type, data_summary, time_range_hours)
            
            # Call AI model
            if self.api_key:
                chat = LlmChat(
                    api_key=self.api_key,
                    session_id=f"analysis_{datetime.now(timezone.utc).timestamp()}",
                    system_message="Eres un experto agrónomo especializado en el cultivo de mandarina (Citrus reticulata). Analizas datos de sensores microclimáticos y proporcionas recomendaciones precisas basadas en las condiciones óptimas para el cultivo de cítricos."
                ).with_model(self.provider, self.model)
                
                user_message = UserMessage(text=prompt)
                response = await chat.send_message(user_message)
                
                # Parse AI response
                analysis_result = self._parse_ai_response(response, data_summary)
            else:
                # Fallback to rule-based analysis
                analysis_result = self._rule_based_analysis(data_summary)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            # Return fallback analysis
            return self._fallback_analysis()
    
    def _prepare_data_summary(self, temperature_data: List[Dict], 
                             humidity_data: List[Dict],
                             soil_moisture_data: List[Dict],
                             luminosity_data: List[Dict]) -> Dict[str, Any]:
        """Prepare data summary for AI analysis"""
        def calculate_stats(data: List[Dict]) -> Dict[str, float]:
            if not data:
                return {"min": 0, "max": 0, "avg": 0, "current": 0}
            values = [d["value"] for d in data]
            return {
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "avg": round(sum(values) / len(values), 2),
                "current": round(values[-1], 2) if values else 0
            }
        
        return {
            "temperature": calculate_stats(temperature_data),
            "air_humidity": calculate_stats(humidity_data),
            "soil_moisture": calculate_stats(soil_moisture_data),
            "luminosity": calculate_stats(luminosity_data),
            "data_points": len(temperature_data)
        }
    
    def _create_analysis_prompt(self, analysis_type: str, data_summary: Dict, time_range_hours: int) -> str:
        """Create prompt for AI analysis"""
        prompt = f"""Analiza los siguientes datos de sensores de un cultivo de mandarina (Citrus reticulata) de las últimas {time_range_hours} horas:

DATOS RECOPILADOS:
- Temperatura: Min={data_summary['temperature']['min']}°C, Max={data_summary['temperature']['max']}°C, Promedio={data_summary['temperature']['avg']}°C, Actual={data_summary['temperature']['current']}°C
- Humedad del aire: Min={data_summary['air_humidity']['min']}%, Max={data_summary['air_humidity']['max']}%, Promedio={data_summary['air_humidity']['avg']}%, Actual={data_summary['air_humidity']['current']}%
- Humedad del suelo: Min={data_summary['soil_moisture']['min']}%, Max={data_summary['soil_moisture']['max']}%, Promedio={data_summary['soil_moisture']['avg']}%, Actual={data_summary['soil_moisture']['current']}%
- Luminosidad: Min={data_summary['luminosity']['min']} lux, Max={data_summary['luminosity']['max']} lux, Promedio={data_summary['luminosity']['avg']} lux, Actual={data_summary['luminosity']['current']} lux

CONDICIONES ÓPTIMAS PARA MANDARINA:
- Temperatura: 20-30°C (óptimo: 23-28°C)
- Humedad relativa: 60-80%
- Humedad del suelo: 40-70%
- Luminosidad: 30,000-50,000 lux

Proporciona tu respuesta en formato JSON con la siguiente estructura:
{{
  "summary": "Resumen breve del estado general del cultivo",
  "predictions": [
    {{"parameter": "nombre", "trend": "increasing/decreasing/stable", "forecast": "descripción"}}
  ],
  "recommendations": ["recomendación 1", "recomendación 2", "recomendación 3"],
  "risk_level": "low/medium/high/critical",
  "alerts": ["alerta importante si existe"]
}}

Respuesta (solo JSON, sin texto adicional):"""
        
        return prompt
    
    def _parse_ai_response(self, response: str, data_summary: Dict) -> Dict[str, Any]:
        """Parse AI response"""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                return {
                    "analysis_type": "ai_powered",
                    "summary": parsed.get("summary", ""),
                    "predictions": parsed.get("predictions", []),
                    "recommendations": parsed.get("recommendations", []),
                    "risk_level": parsed.get("risk_level", "medium"),
                    "alerts": parsed.get("alerts", []),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "data_summary": data_summary
                }
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
        
        # Fallback
        return self._rule_based_analysis(data_summary)
    
    def _rule_based_analysis(self, data_summary: Dict) -> Dict[str, Any]:
        """Rule-based fallback analysis"""
        recommendations = []
        alerts = []
        risk_level = "low"
        
        temp = data_summary["temperature"]["current"]
        air_hum = data_summary["air_humidity"]["current"]
        soil_moist = data_summary["soil_moisture"]["current"]
        lux = data_summary["luminosity"]["current"]
        
        # Temperature analysis
        if temp > 32:
            risk_level = "high"
            alerts.append("Temperatura excesivamente alta detectada")
            recommendations.append("Implementar riego por aspersión para reducir temperatura ambiental")
        elif temp < 18:
            risk_level = "medium" if risk_level == "low" else risk_level
            alerts.append("Temperatura baja detectada")
            recommendations.append("Proteger cultivo de posibles heladas")
        
        # Soil moisture analysis
        if soil_moist < 35:
            risk_level = "high" if risk_level != "critical" else risk_level
            alerts.append("Humedad del suelo crítica - riesgo de estrés hídrico")
            recommendations.append("Aumentar frecuencia de riego inmediatamente")
        elif soil_moist > 75:
            risk_level = "medium" if risk_level == "low" else risk_level
            recommendations.append("Reducir riego para evitar saturación del suelo")
        
        # Air humidity analysis
        if air_hum < 55:
            recommendations.append("Considerar nebulización para aumentar humedad ambiental")
        
        # Luminosity analysis
        if lux > 55000:
            recommendations.append("Alta radiación solar - monitorear estrés por luz")
        elif lux < 25000:
            recommendations.append("Luminosidad baja - verificar sombreado excesivo")
        
        # Default recommendation
        if not recommendations:
            recommendations.append("Condiciones dentro de parámetros normales - mantener monitoreo regular")
        
        summary = f"Análisis de condiciones: Temperatura {temp}°C, Humedad suelo {soil_moist}%, Humedad aire {air_hum}%, Luminosidad {lux} lux"
        
        return {
            "analysis_type": "rule_based",
            "summary": summary,
            "predictions": [
                {"parameter": "temperature", "trend": "stable", "forecast": "Se espera estabilidad térmica"},
                {"parameter": "soil_moisture", "trend": "stable", "forecast": "Mantener programa de riego actual"}
            ],
            "recommendations": recommendations,
            "risk_level": risk_level,
            "alerts": alerts,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_summary": data_summary
        }
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Complete fallback analysis"""
        return {
            "analysis_type": "fallback",
            "summary": "Sistema de análisis en modo básico - datos limitados disponibles",
            "predictions": [],
            "recommendations": ["Verificar conectividad de sensores", "Revisar configuración del sistema"],
            "risk_level": "medium",
            "alerts": ["Sistema de análisis operando en modo limitado"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_summary": {}
        }

ai_analyzer = AIAnalyzer()