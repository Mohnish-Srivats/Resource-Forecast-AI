import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, date, timedelta
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

from ..models.license_models import SoftwareLicense, UsageMetric, ForecastData, Recommendation



class LicenseUtilizationAnalyzer:
    """AI Agent for analyzing software license utilization patterns"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.forecast_models = {}
        
    def analyze_utilization_patterns(self, usage_data: List[UsageMetric]) -> Dict[str, Any]:
        """
        Analyze utilization patterns from historical usage data
        """
        if not usage_data:
            return {"error": "No usage data provided"}
            
        df = pd.DataFrame([metric.model_dump() for metric in usage_data])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        analysis = {
            "total_records": len(df),
            "date_range": {
                "start": df['date'].min().strftime('%Y-%m-%d'),
                "end": df['date'].max().strftime('%Y-%m-%d')
            },
            "utilization_stats": {
                "mean": float(df['utilization_percentage'].mean()),
                "median": float(df['utilization_percentage'].median()),
                "std": float(df['utilization_percentage'].std()),
                "min": float(df['utilization_percentage'].min()),
                "max": float(df['utilization_percentage'].max())
            },
            "cost_analysis": {
                "total_cost": float(df['cost_incurred'].sum()),
                "average_daily_cost": float(df['cost_incurred'].mean()),
                "cost_trend": self._calculate_trend(df['cost_incurred'].values)
            },
            "usage_trends": self._analyze_usage_trends(df),
            "anomalies": self._detect_anomalies(df),
            "seasonality": self._detect_seasonality(df)
        }
        
        return analysis
    
    def _calculate_trend(self, values: np.ndarray) -> str:
        """Calculate trend direction from time series data"""
        if len(values) < 2:
            return "insufficient_data"
            
        # Simple linear trend calculation
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_usage_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze usage trends over time"""
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
        df['quarter'] = df['date'].dt.quarter
        
        trends = {
            "monthly_pattern": df.groupby('month')['utilization_percentage'].mean().to_dict(),
            "weekly_pattern": df.groupby('day_of_week')['utilization_percentage'].mean().to_dict(),
            "quarterly_pattern": df.groupby('quarter')['utilization_percentage'].mean().to_dict(),
            "growth_rate": self._calculate_growth_rate(df['utilization_percentage'].values)
        }
        
        return trends
    
    def _calculate_growth_rate(self, values: np.ndarray) -> float:
        """Calculate compound growth rate"""
        if len(values) < 2:
            return 0.0
            
        first_value = values[0]
        last_value = values[-1]
        periods = len(values) - 1
        
        if first_value == 0:
            return 0.0
            
        growth_rate = ((last_value / first_value) ** (1/periods)) - 1
        return float(growth_rate)
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalous usage patterns"""
        if len(df) < 10:
            return []
            
        # Prepare features for anomaly detection
        features = df[['utilization_percentage', 'cost_incurred', 'units_used']].values
        features_scaled = self.scaler.fit_transform(features)
        
        # Detect anomalies
        anomaly_scores = self.anomaly_detector.fit_predict(features_scaled)
        anomalies = []
        
        for i, score in enumerate(anomaly_scores):
            if score == -1:  # Anomaly detected
                anomalies.append({
                    "date": df.iloc[i]['date'].strftime('%Y-%m-%d'),
                    "utilization": float(df.iloc[i]['utilization_percentage']),
                    "cost": float(df.iloc[i]['cost_incurred']),
                    "anomaly_score": float(self.anomaly_detector.score_samples([features_scaled[i]])[0])
                })
        
        return anomalies
    
    def _detect_seasonality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect seasonal patterns in usage"""
        if len(df) < 30:  # Need at least a month of data
            return {"insufficient_data": True}
            
        df['month'] = df['date'].dt.month
        monthly_avg = df.groupby('month')['utilization_percentage'].mean()
        
        # Calculate seasonality strength
        seasonal_variance = monthly_avg.var()
        overall_variance = df['utilization_percentage'].var()
        seasonality_strength = seasonal_variance / overall_variance if overall_variance > 0 else 0
        
        return {
            "strength": float(seasonality_strength),
            "monthly_pattern": monthly_avg.to_dict(),
            "peak_month": int(monthly_avg.idxmax()),
            "low_month": int(monthly_avg.idxmin())
        }


class LicenseForecastingAgent:
    """AI Agent for forecasting license usage and costs"""
    
    def __init__(self):
        self.models = {}
        
    def generate_forecast(self, usage_data: List[UsageMetric], 
                         license_info: SoftwareLicense, 
                         forecast_days: int = 90) -> List[ForecastData]:
        """
        Generate usage and cost forecasts for a software license
        """
        if not usage_data:
            return []
            
        df = pd.DataFrame([metric.model_dump() for metric in usage_data])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Prepare time series data
        df.set_index('date', inplace=True)
        
        forecasts = []
        
        # Forecast usage
        usage_forecast = self._forecast_usage(df, forecast_days)
        
        # Forecast costs
        cost_forecast = self._forecast_costs(df, license_info, forecast_days)
        
        # Generate forecast data points
        for i in range(forecast_days):
            forecast_date = datetime.now().date() + timedelta(days=i+1)
            
            forecast = ForecastData(
                license_id=license_info.id,
                forecast_date=forecast_date,
                predicted_usage=float(usage_forecast[i]) if i < len(usage_forecast) else 0,
                predicted_cost=float(cost_forecast[i]) if i < len(cost_forecast) else 0,
                confidence_score=self._calculate_confidence(df, i),
                trend=self._determine_trend(df, usage_forecast),
                seasonal_factors=self._get_seasonal_factors(forecast_date)
            )
            forecasts.append(forecast)
        
        return forecasts
    
    def _forecast_usage(self, df: pd.DataFrame, days: int) -> np.ndarray:
        """Forecast usage using time series analysis"""
        if len(df) < 7:
            # Not enough data, return simple average
            avg_usage = df['units_used'].mean()
            return np.full(days, avg_usage)
        
        # Simple moving average with trend
        window = min(7, len(df) // 2)
        recent_avg = df['units_used'].tail(window).mean()
        
        # Calculate trend
        if len(df) >= 14:
            old_avg = df['units_used'].head(window).mean()
            trend = (recent_avg - old_avg) / len(df)
        else:
            trend = 0
        
        # Generate forecast
        forecast = []
        for i in range(days):
            predicted_value = recent_avg + (trend * (i + 1))
            # Add some seasonality (simplified)
            seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * i / 30)  # Monthly cycle
            forecast.append(predicted_value * seasonal_factor)
        
        return np.array(forecast)
    
    def _forecast_costs(self, df: pd.DataFrame, license_info: SoftwareLicense, days: int) -> np.ndarray:
        """Forecast costs based on usage and billing model"""
        usage_forecast = self._forecast_usage(df, days)
        
        if license_info.billing_type == "per_task":
            return usage_forecast * license_info.cost_per_unit
        elif license_info.billing_type == "flat_rate":
            daily_cost = license_info.total_license_cost / (license_info.license_period_months * 30)
            return np.full(days, daily_cost)
        else:
            # Default to per-user or other models
            return usage_forecast * license_info.cost_per_unit
    
    def _calculate_confidence(self, df: pd.DataFrame, forecast_day: int) -> float:
        """Calculate confidence score for forecast"""
        if len(df) < 7:
            return 0.3
        
        # Confidence decreases with forecast horizon
        base_confidence = 0.8
        decay_factor = 0.95
        confidence = base_confidence * (decay_factor ** forecast_day)
        
        # Adjust based on data quality
        data_consistency = 1 - (df['units_used'].std() / df['units_used'].mean()) if df['units_used'].mean() > 0 else 0.5
        confidence *= data_consistency
        
        return max(0.1, min(0.95, confidence))
    
    def _determine_trend(self, df: pd.DataFrame, forecast: np.ndarray) -> str:
        """Determine overall trend from historical data and forecast"""
        if len(df) < 7:
            return "stable"
        
        recent_avg = df['units_used'].tail(7).mean()
        forecast_avg = np.mean(forecast[:7]) if len(forecast) >= 7 else np.mean(forecast)
        
        change_percent = (forecast_avg - recent_avg) / recent_avg if recent_avg > 0 else 0
        
        if change_percent > 0.1:
            return "upward"
        elif change_percent < -0.1:
            return "downward"
        else:
            return "stable"
    
    def _get_seasonal_factors(self, forecast_date: date) -> Dict[str, float]:
        """Get seasonal factors for the forecast date"""
        month = forecast_date.month
        day_of_week = forecast_date.weekday()
        
        # Simplified seasonal factors
        monthly_factor = 1 + 0.1 * np.sin(2 * np.pi * (month - 1) / 12)
        weekly_factor = 1 + 0.05 * np.sin(2 * np.pi * day_of_week / 7)
        
        return {
            "monthly": float(monthly_factor),
            "weekly": float(weekly_factor)
        }


class RecommendationEngine:
    """AI Agent for generating license renewal recommendations"""
    
    def __init__(self):
        self.utilization_analyzer = LicenseUtilizationAnalyzer()
        self.forecasting_agent = LicenseForecastingAgent()
    
    def generate_recommendations(self, license_info: SoftwareLicense, 
                               usage_data: List[UsageMetric]) -> Recommendation:
        """
        Generate renewal recommendations based on license and usage analysis
        """
        # Analyze current utilization
        utilization_analysis = self.utilization_analyzer.analyze_utilization_patterns(usage_data)
        
        # Generate forecasts
        forecasts = self.forecasting_agent.generate_forecast(usage_data, license_info, 90)
        
        # Calculate key metrics
        avg_utilization = utilization_analysis.get('utilization_stats', {}).get('mean', 0)
        cost_trend = utilization_analysis.get('cost_analysis', {}).get('cost_trend', 'stable')
        anomalies = utilization_analysis.get('anomalies', [])
        
        # Determine recommendation
        recommendation, confidence, reasoning = self._evaluate_license(license_info, 
                                                                      avg_utilization, 
                                                                      cost_trend, 
                                                                      forecasts,
                                                                      anomalies)
        
        # Calculate potential savings
        estimated_savings = self._calculate_savings(license_info, recommendation, forecasts)
        
        # Identify risk factors
        risk_factors = self._identify_risks(license_info, utilization_analysis, forecasts)
        
        # Generate alternative options
        alternatives = self._suggest_alternatives(license_info, avg_utilization, forecasts)
        
        return Recommendation(
            license_id=license_info.id,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            estimated_savings=estimated_savings,
            risk_factors=risk_factors,
            alternative_options=alternatives,
            priority=self._determine_priority(confidence, estimated_savings, risk_factors)
        )
    
    def _evaluate_license(self, license_info: SoftwareLicense, avg_utilization: float, 
                         cost_trend: str, forecasts: List[ForecastData], 
                         anomalies: List[Dict]) -> Tuple[str, float, List[str]]:
        """Evaluate license and determine recommendation"""
        reasoning = []
        confidence = 0.7
        
        # Utilization-based evaluation
        if avg_utilization < 30:
            reasoning.append(f"Low utilization ({avg_utilization:.1f}%) suggests over-provisioning")
            if avg_utilization < 20:
                recommendation = "cancel"
                confidence = 0.9
            else:
                recommendation = "downgrade"
                confidence = 0.8
        elif avg_utilization > 90:
            reasoning.append(f"High utilization ({avg_utilization:.1f}%) may require upgrade")
            recommendation = "negotiate"
            confidence = 0.8
        else:
            reasoning.append(f"Moderate utilization ({avg_utilization:.1f}%) is within acceptable range")
            recommendation = "renew"
            confidence = 0.7
        
        # Cost trend analysis
        if cost_trend == "increasing":
            reasoning.append("Increasing cost trend detected")
            if recommendation == "renew":
                recommendation = "negotiate"
                confidence = min(confidence + 0.1, 0.95)
        elif cost_trend == "decreasing":
            reasoning.append("Decreasing cost trend suggests good value")
            confidence = min(confidence + 0.05, 0.95)
        
        # Anomaly detection
        if len(anomalies) > 3:
            reasoning.append(f"Multiple usage anomalies detected ({len(anomalies)})")
            confidence = max(confidence - 0.1, 0.3)
        
        # Forecast analysis
        if forecasts:
            avg_forecast_usage = np.mean([f.predicted_usage for f in forecasts])
            current_usage = np.mean([f.predicted_usage for f in forecasts[:7]]) if len(forecasts) >= 7 else avg_forecast_usage
            
            if avg_forecast_usage > current_usage * 1.2:
                reasoning.append("Forecast predicts significant usage increase")
                if recommendation == "cancel":
                    recommendation = "renew"
            elif avg_forecast_usage < current_usage * 0.8:
                reasoning.append("Forecast predicts usage decrease")
                if recommendation == "renew":
                    recommendation = "downgrade"
        
        return recommendation, confidence, reasoning
    
    def _calculate_savings(self, license_info: SoftwareLicense, recommendation: str, 
                          forecasts: List[ForecastData]) -> Optional[float]:
        """Calculate potential savings from recommendation"""
        if not forecasts:
            return None
            
        current_annual_cost = license_info.total_license_cost * (12 / license_info.license_period_months)
        
        if recommendation == "cancel":
            return current_annual_cost
        elif recommendation == "downgrade":
            # Assume 30% cost reduction for downgrade
            return current_annual_cost * 0.3
        elif recommendation == "negotiate":
            # Assume 15% cost reduction through negotiation
            return current_annual_cost * 0.15
        else:
            return 0.0
    
    def _identify_risks(self, license_info: SoftwareLicense, utilization_analysis: Dict, 
                       forecasts: List[ForecastData]) -> List[str]:
        """Identify potential risks"""
        risks = []
        
        # High utilization risk
        avg_utilization = utilization_analysis.get('utilization_stats', {}).get('mean', 0)
        if avg_utilization > 85:
            risks.append("High utilization may lead to service degradation")
        
        # Cost trend risk
        cost_trend = utilization_analysis.get('cost_analysis', {}).get('cost_trend', 'stable')
        if cost_trend == "increasing":
            risks.append("Increasing costs may impact budget")
        
        # Anomaly risk
        anomalies = utilization_analysis.get('anomalies', [])
        if len(anomalies) > 2:
            risks.append("Usage anomalies may indicate operational issues")
        
        # Contract risk
        days_to_expiry = (license_info.end_date - datetime.now().date()).days
        if days_to_expiry < 30:
            risks.append("License expires soon - urgent action required")
        
        return risks
    
    def _suggest_alternatives(self, license_info: SoftwareLicense, avg_utilization: float, 
                             forecasts: List[ForecastData]) -> List[Dict[str, Any]]:
        """Suggest alternative options"""
        alternatives = []
        
        if avg_utilization < 50:
            alternatives.append({
                "option": "Pay-per-use model",
                "description": "Switch to usage-based billing to reduce costs",
                "estimated_savings": license_info.total_license_cost * 0.4
            })
        
        if avg_utilization > 80:
            alternatives.append({
                "option": "Enterprise license",
                "description": "Upgrade to enterprise license for better rates",
                "estimated_savings": -license_info.total_license_cost * 0.2  # Negative = cost increase
            })
        
        alternatives.append({
            "option": "Multi-year contract",
            "description": "Sign longer contract for better pricing",
            "estimated_savings": license_info.total_license_cost * 0.1
        })
        
        return alternatives
    
    def _determine_priority(self, confidence: float, estimated_savings: Optional[float], 
                           risk_factors: List[str]) -> str:
        """Determine recommendation priority"""
        if len(risk_factors) > 2 or (estimated_savings and estimated_savings > 10000):
            return "high"
        elif confidence > 0.8 or (estimated_savings and estimated_savings > 5000):
            return "medium"
        else:
            return "low"
