from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
import json

from ..models.chat_models import Intent, ReportCustomization, CustomReportRequest
from ..models.license_models import SoftwareLicense, UsageMetric
from .ai_agent import RecommendationEngine, LicenseUtilizationAnalyzer, LicenseForecastingAgent
from ..utils.data_manager import DataManager


class ReportCustomizer:
    """Custom report generation based on user intents and preferences"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.recommendation_engine = RecommendationEngine()
        self.utilization_analyzer = LicenseUtilizationAnalyzer()
        self.forecasting_agent = LicenseForecastingAgent()
    
    def generate_custom_report(self, intent: Intent, user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a custom report based on intent and user preferences"""
        
        # Determine report type and customization
        customization = self._create_customization(intent, user_preferences)
        
        # Get relevant data
        licenses = self._get_filtered_licenses(intent, customization)
        usage_data = self._get_filtered_usage_data(intent, customization)
        
        # Generate report based on intent category
        if intent.category.value == "dashboard":
            return self._generate_dashboard_report(licenses, usage_data, customization)
        elif intent.category.value == "report":
            return self._generate_custom_report_data(licenses, usage_data, customization, intent)
        elif intent.category.value == "analysis":
            return self._generate_analysis_report(licenses, usage_data, customization, intent)
        elif intent.category.value == "recommendation":
            return self._generate_recommendation_report(licenses, usage_data, customization, intent)
        elif intent.category.value == "forecast":
            return self._generate_forecast_report(licenses, usage_data, customization, intent)
        elif intent.category.value == "comparison":
            return self._generate_comparison_report(licenses, usage_data, customization, intent)
        else:
            return self._generate_general_report(licenses, usage_data, customization)
    
    def _create_customization(self, intent: Intent, user_preferences: Optional[Dict[str, Any]]) -> ReportCustomization:
        """Create customization object from intent and preferences"""
        customization = ReportCustomization()
        
        # Set time period
        if intent.entities.get("time_period"):
            time_period = intent.entities["time_period"]
            if time_period["type"] == "days":
                customization.time_period = f"last_{time_period['value']}_days"
            elif time_period["type"] == "month":
                customization.time_period = "last_month"
            elif time_period["type"] == "quarter":
                customization.time_period = f"q{time_period['value']}"
        
        # Set license filters
        if intent.entities.get("licenses"):
            customization.license_filters = intent.entities["licenses"]
        
        # Set metric focus
        if intent.entities.get("metrics"):
            customization.metric_focus = intent.entities["metrics"]
        
        # Set team perspective
        if intent.entities.get("teams"):
            customization.team_perspective = intent.entities["teams"][0]
        
        # Set detail level
        if intent.parameters.get("detail_level"):
            customization.detail_level = intent.parameters["detail_level"]
        
        # Set other preferences
        customization.include_forecasts = intent.parameters.get("include_forecasts", True)
        customization.include_recommendations = intent.parameters.get("include_recommendations", True)
        customization.include_visualizations = intent.parameters.get("include_visualizations", True)
        
        # Apply user preferences
        if user_preferences:
            for key, value in user_preferences.items():
                if hasattr(customization, key):
                    setattr(customization, key, value)
        
        return customization
    
    def _get_filtered_licenses(self, intent: Intent, customization: ReportCustomization) -> List[SoftwareLicense]:
        """Get licenses filtered by intent and customization"""
        all_licenses = self.data_manager.get_all_licenses()
        
        if not customization.license_filters:
            return all_licenses
        
        # Filter by license names
        filtered_licenses = []
        for license_info in all_licenses:
            for filter_name in customization.license_filters:
                if filter_name.lower() in license_info.name.lower() or filter_name.lower() in license_info.vendor.lower():
                    filtered_licenses.append(license_info)
                    break
        
        return filtered_licenses if filtered_licenses else all_licenses
    
    def _get_filtered_usage_data(self, intent: Intent, customization: ReportCustomization) -> List[UsageMetric]:
        """Get usage data filtered by intent and customization"""
        all_usage_data = self.data_manager.get_all_usage_metrics()
        
        # Filter by time period
        if customization.time_period:
            if customization.time_period.startswith("last_"):
                days = int(customization.time_period.split("_")[1])
                cutoff_date = date.today() - timedelta(days=days)
                all_usage_data = [m for m in all_usage_data if m.date >= cutoff_date]
        
        # Filter by license IDs if specific licenses are requested
        if customization.license_filters:
            filtered_licenses = self._get_filtered_licenses(intent, customization)
            license_ids = [l.id for l in filtered_licenses]
            all_usage_data = [m for m in all_usage_data if m.license_id in license_ids]
        
        return all_usage_data
    
    def _generate_dashboard_report(self, licenses: List[SoftwareLicense], 
                                 usage_data: List[UsageMetric], 
                                 customization: ReportCustomization) -> Dict[str, Any]:
        """Generate dashboard-style report"""
        total_cost = sum(license.total_license_cost for license in licenses)
        avg_utilization = sum(metric.utilization_percentage for metric in usage_data) / len(usage_data) if usage_data else 0
        
        return {
            "report_type": "dashboard",
            "summary": {
                "total_licenses": len(licenses),
                "total_cost": total_cost,
                "average_utilization": avg_utilization,
                "time_period": customization.time_period or "all_time"
            },
            "key_metrics": self._calculate_key_metrics(licenses, usage_data),
            "visualizations": self._generate_visualizations(licenses, usage_data, customization) if customization.include_visualizations else [],
            "insights": self._generate_insights(licenses, usage_data)
        }
    
    def _generate_custom_report_data(self, licenses: List[SoftwareLicense], 
                                   usage_data: List[UsageMetric], 
                                   customization: ReportCustomization,
                                   intent: Intent) -> Dict[str, Any]:
        """Generate custom report based on team perspective"""
        
        if customization.team_perspective == "ap":
            return self._generate_ap_team_report(licenses, usage_data, customization)
        elif customization.team_perspective == "procurement":
            return self._generate_procurement_team_report(licenses, usage_data, customization)
        elif customization.team_perspective == "executive":
            return self._generate_executive_report(licenses, usage_data, customization)
        else:
            return self._generate_general_team_report(licenses, usage_data, customization)
    
    def _generate_analysis_report(self, licenses: List[SoftwareLicense], 
                                usage_data: List[UsageMetric], 
                                customization: ReportCustomization,
                                intent: Intent) -> Dict[str, Any]:
        """Generate detailed analysis report"""
        
        analysis_results = []
        
        for license_info in licenses:
            license_usage = [m for m in usage_data if m.license_id == license_info.id]
            if license_usage:
                analysis = self.utilization_analyzer.analyze_utilization_patterns(license_usage)
                analysis_results.append({
                    "license": license_info.name,
                    "analysis": analysis
                })
        
        return {
            "report_type": "analysis",
            "focus": intent.entities.get("metrics", ["cost", "usage"]),
            "time_period": customization.time_period,
            "detailed_analysis": analysis_results,
            "summary_insights": self._generate_analysis_insights(analysis_results),
            "visualizations": self._generate_analysis_visualizations(analysis_results, customization) if customization.include_visualizations else []
        }
    
    def _generate_recommendation_report(self, licenses: List[SoftwareLicense], 
                                      usage_data: List[UsageMetric], 
                                      customization: ReportCustomization,
                                      intent: Intent) -> Dict[str, Any]:
        """Generate recommendation-focused report"""
        
        recommendations = []
        total_savings = 0
        
        for license_info in licenses:
            license_usage = [m for m in usage_data if m.license_id == license_info.id]
            if license_usage:
                rec = self.recommendation_engine.generate_recommendations(license_info, license_usage)
                recommendations.append({
                    "license": license_info.name,
                    "recommendation": rec.recommendation,
                    "confidence": rec.confidence,
                    "estimated_savings": rec.estimated_savings or 0,
                    "reasoning": rec.reasoning,
                    "priority": rec.priority
                })
                total_savings += rec.estimated_savings or 0
        
        # Sort by priority and savings
        recommendations.sort(key=lambda x: (x["priority"] == "high", x["estimated_savings"]), reverse=True)
        
        return {
            "report_type": "recommendations",
            "total_potential_savings": total_savings,
            "recommendations": recommendations,
            "priority_actions": [r for r in recommendations if r["priority"] == "high"],
            "summary": self._generate_recommendation_summary(recommendations, total_savings)
        }
    
    def _generate_forecast_report(self, licenses: List[SoftwareLicense], 
                                usage_data: List[UsageMetric], 
                                customization: ReportCustomization,
                                intent: Intent) -> Dict[str, Any]:
        """Generate forecast-focused report"""
        
        forecasts = []
        
        for license_info in licenses:
            license_usage = [m for m in usage_data if m.license_id == license_info.id]
            if license_usage:
                forecast_data = self.forecasting_agent.generate_forecast(license_usage, license_info, 90)
                forecasts.append({
                    "license": license_info.name,
                    "forecasts": forecast_data,
                    "summary": self._summarize_forecasts(forecast_data)
                })
        
        return {
            "report_type": "forecast",
            "forecast_horizon": "90_days",
            "license_forecasts": forecasts,
            "overall_trends": self._analyze_overall_trends(forecasts),
            "confidence_scores": self._calculate_forecast_confidence(forecasts)
        }
    
    def _generate_comparison_report(self, licenses: List[SoftwareLicense], 
                                  usage_data: List[UsageMetric], 
                                  customization: ReportCustomization,
                                  intent: Intent) -> Dict[str, Any]:
        """Generate comparison report between licenses"""
        
        if len(licenses) < 2:
            return {"error": "Need at least 2 licenses to compare"}
        
        comparison_data = []
        
        for license_info in licenses:
            license_usage = [m for m in usage_data if m.license_id == license_info.id]
            if license_usage:
                avg_utilization = sum(m.utilization_percentage for m in license_usage) / len(license_usage)
                total_cost = license_info.total_license_cost
                
                comparison_data.append({
                    "license": license_info.name,
                    "vendor": license_info.vendor,
                    "cost": total_cost,
                    "utilization": avg_utilization,
                    "cost_per_unit": license_info.cost_per_unit,
                    "efficiency_score": avg_utilization / (total_cost / 1000) if total_cost > 0 else 0
                })
        
        return {
            "report_type": "comparison",
            "licenses_compared": len(licenses),
            "comparison_data": comparison_data,
            "rankings": self._generate_rankings(comparison_data),
            "insights": self._generate_comparison_insights(comparison_data)
        }
    
    def _generate_general_report(self, licenses: List[SoftwareLicense], 
                               usage_data: List[UsageMetric], 
                               customization: ReportCustomization) -> Dict[str, Any]:
        """Generate general purpose report"""
        
        return {
            "report_type": "general",
            "summary": {
                "total_licenses": len(licenses),
                "total_cost": sum(license.total_license_cost for license in licenses),
                "average_utilization": sum(metric.utilization_percentage for metric in usage_data) / len(usage_data) if usage_data else 0
            },
            "licenses": [{"name": l.name, "cost": l.total_license_cost, "utilization": l.current_units / l.max_units * 100 if l.max_units else 0} for l in licenses],
            "insights": self._generate_insights(licenses, usage_data)
        }
    
    def _calculate_key_metrics(self, licenses: List[SoftwareLicense], usage_data: List[UsageMetric]) -> Dict[str, Any]:
        """Calculate key performance metrics"""
        total_cost = sum(license.total_license_cost for license in licenses)
        avg_utilization = sum(metric.utilization_percentage for metric in usage_data) / len(usage_data) if usage_data else 0
        
        # Calculate cost efficiency
        high_utilization_licenses = [l for l in licenses if l.current_units and l.max_units and (l.current_units / l.max_units) > 0.8]
        low_utilization_licenses = [l for l in licenses if l.current_units and l.max_units and (l.current_units / l.max_units) < 0.3]
        
        return {
            "total_annual_cost": total_cost,
            "average_utilization": avg_utilization,
            "high_utilization_count": len(high_utilization_licenses),
            "low_utilization_count": len(low_utilization_licenses),
            "cost_efficiency_score": avg_utilization / (total_cost / 10000) if total_cost > 0 else 0
        }
    
    def _generate_visualizations(self, licenses: List[SoftwareLicense], 
                               usage_data: List[UsageMetric], 
                               customization: ReportCustomization) -> List[Dict[str, Any]]:
        """Generate visualization data"""
        visualizations = []
        
        # Cost trend chart
        if customization.metric_focus is None or "cost" in customization.metric_focus:
            cost_trend = self.data_manager.get_cost_trend_data(30)
            visualizations.append({
                "type": "line_chart",
                "title": "Cost Trend (Last 30 Days)",
                "data": cost_trend
            })
        
        # Utilization distribution
        if customization.metric_focus is None or "utilization" in customization.metric_focus:
            utilization_dist = self.data_manager.get_utilization_distribution()
            visualizations.append({
                "type": "bar_chart",
                "title": "Utilization Distribution",
                "data": utilization_dist
            })
        
        return visualizations
    
    def _generate_insights(self, licenses: List[SoftwareLicense], usage_data: List[UsageMetric]) -> List[str]:
        """Generate key insights from the data"""
        insights = []
        
        total_cost = sum(license.total_license_cost for license in licenses)
        avg_utilization = sum(metric.utilization_percentage for metric in usage_data) / len(usage_data) if usage_data else 0
        
        if avg_utilization < 50:
            insights.append(f"Overall utilization is low at {avg_utilization:.1f}%, indicating potential for cost optimization")
        
        high_cost_licenses = [l for l in licenses if l.total_license_cost > total_cost * 0.2]
        if high_cost_licenses:
            insights.append(f"Top cost driver: {high_cost_licenses[0].name} accounts for ${high_cost_licenses[0].total_license_cost:,.0f}")
        
        low_utilization_licenses = [l for l in licenses if l.current_units and l.max_units and (l.current_units / l.max_units) < 0.3]
        if low_utilization_licenses:
            insights.append(f"{len(low_utilization_licenses)} licenses have utilization below 30% - consider downsizing or cancellation")
        
        return insights
    
    def _generate_ap_team_report(self, licenses: List[SoftwareLicense], 
                               usage_data: List[UsageMetric], 
                               customization: ReportCustomization) -> Dict[str, Any]:
        """Generate AP team focused report"""
        # This would integrate with the existing AP report logic
        return {
            "report_type": "ap_team",
            "focus": "financial_planning",
            "upcoming_renewals": self._get_upcoming_renewals(licenses),
            "budget_impact": self._calculate_budget_impact(licenses),
            "payment_schedule": self._generate_payment_schedule(licenses)
        }
    
    def _generate_procurement_team_report(self, licenses: List[SoftwareLicense], 
                                        usage_data: List[UsageMetric], 
                                        customization: ReportCustomization) -> Dict[str, Any]:
        """Generate procurement team focused report"""
        return {
            "report_type": "procurement",
            "focus": "vendor_management",
            "vendor_analysis": self._analyze_vendors(licenses),
            "negotiation_opportunities": self._identify_negotiation_opportunities(licenses, usage_data),
            "market_benchmarks": self._generate_market_benchmarks(licenses)
        }
    
    def _generate_executive_report(self, licenses: List[SoftwareLicense], 
                                 usage_data: List[UsageMetric], 
                                 customization: ReportCustomization) -> Dict[str, Any]:
        """Generate executive summary report"""
        return {
            "report_type": "executive",
            "focus": "strategic_overview",
            "executive_summary": self._generate_executive_summary(licenses, usage_data),
            "key_metrics": self._calculate_key_metrics(licenses, usage_data),
            "strategic_recommendations": self._generate_strategic_recommendations(licenses, usage_data)
        }
    
    def _generate_general_team_report(self, licenses: List[SoftwareLicense], 
                                    usage_data: List[UsageMetric], 
                                    customization: ReportCustomization) -> Dict[str, Any]:
        """Generate general team report"""
        return {
            "report_type": "general_team",
            "summary": self._generate_team_summary(licenses, usage_data),
            "insights": self._generate_insights(licenses, usage_data),
            "recommendations": self._generate_quick_recommendations(licenses, usage_data)
        }
    
    # Helper methods for report generation
    def _get_upcoming_renewals(self, licenses: List[SoftwareLicense]) -> List[Dict[str, Any]]:
        """Get upcoming license renewals"""
        upcoming = []
        for license_info in licenses:
            days_to_expiry = (license_info.end_date - date.today()).days
            if 0 <= days_to_expiry <= 90:
                upcoming.append({
                    "license": license_info.name,
                    "expiry_date": license_info.end_date.isoformat(),
                    "days_to_expiry": days_to_expiry,
                    "cost": license_info.total_license_cost
                })
        return upcoming
    
    def _calculate_budget_impact(self, licenses: List[SoftwareLicense]) -> Dict[str, float]:
        """Calculate budget impact"""
        total_annual = sum(license.total_license_cost * (12 / license.license_period_months) for license in licenses)
        return {
            "total_annual": total_annual,
            "monthly": total_annual / 12,
            "quarterly": total_annual / 4
        }
    
    def _generate_payment_schedule(self, licenses: List[SoftwareLicense]) -> List[Dict[str, Any]]:
        """Generate payment schedule"""
        schedule = []
        for license_info in licenses:
            if license_info.auto_renewal:
                schedule.append({
                    "license": license_info.name,
                    "next_payment": license_info.end_date.isoformat(),
                    "amount": license_info.total_license_cost
                })
        return schedule
    
    def _analyze_vendors(self, licenses: List[SoftwareLicense]) -> Dict[str, Any]:
        """Analyze vendor spending"""
        vendor_analysis = {}
        for license_info in licenses:
            vendor = license_info.vendor
            if vendor not in vendor_analysis:
                vendor_analysis[vendor] = {"count": 0, "total_cost": 0}
            vendor_analysis[vendor]["count"] += 1
            vendor_analysis[vendor]["total_cost"] += license_info.total_license_cost
        return vendor_analysis
    
    def _identify_negotiation_opportunities(self, licenses: List[SoftwareLicense], 
                                          usage_data: List[UsageMetric]) -> List[Dict[str, Any]]:
        """Identify negotiation opportunities"""
        opportunities = []
        for license_info in licenses:
            license_usage = [m for m in usage_data if m.license_id == license_info.id]
            if license_usage:
                avg_utilization = sum(m.utilization_percentage for m in license_usage) / len(license_usage)
                if avg_utilization > 80:
                    opportunities.append({
                        "license": license_info.name,
                        "vendor": license_info.vendor,
                        "utilization": avg_utilization,
                        "opportunity": "High utilization - negotiate for better rates"
                    })
        return opportunities
    
    def _generate_market_benchmarks(self, licenses: List[SoftwareLicense]) -> Dict[str, Any]:
        """Generate market benchmarks"""
        total_cost = sum(license.total_license_cost for license in licenses)
        return {
            "average_license_cost": total_cost / len(licenses) if licenses else 0,
            "total_vendors": len(set(license.vendor for license in licenses)),
            "most_expensive_vendor": max(licenses, key=lambda x: x.total_license_cost).vendor if licenses else None
        }
    
    def _generate_executive_summary(self, licenses: List[SoftwareLicense], 
                                  usage_data: List[UsageMetric]) -> Dict[str, Any]:
        """Generate executive summary"""
        total_cost = sum(license.total_license_cost for license in licenses)
        avg_utilization = sum(metric.utilization_percentage for metric in usage_data) / len(usage_data) if usage_data else 0
        
        return {
            "total_software_spend": total_cost,
            "license_count": len(licenses),
            "average_utilization": avg_utilization,
            "cost_trend": "stable",  # This would be calculated from historical data
            "optimization_potential": "high" if avg_utilization < 60 else "medium"
        }
    
    def _generate_strategic_recommendations(self, licenses: List[SoftwareLicense], 
                                          usage_data: List[UsageMetric]) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        low_utilization_count = len([l for l in licenses if l.current_units and l.max_units and (l.current_units / l.max_units) < 0.3])
        if low_utilization_count > 0:
            recommendations.append(f"Consider consolidating {low_utilization_count} underutilized licenses")
        
        high_cost_licenses = [l for l in licenses if l.total_license_cost > 50000]
        if high_cost_licenses:
            recommendations.append("Negotiate enterprise agreements for high-cost licenses")
        
        recommendations.append("Implement regular utilization reviews to optimize costs")
        
        return recommendations
    
    def _generate_team_summary(self, licenses: List[SoftwareLicense], 
                             usage_data: List[UsageMetric]) -> Dict[str, Any]:
        """Generate team summary"""
        return {
            "total_licenses": len(licenses),
            "total_cost": sum(license.total_license_cost for license in licenses),
            "average_utilization": sum(metric.utilization_percentage for metric in usage_data) / len(usage_data) if usage_data else 0,
            "top_vendor": max(licenses, key=lambda x: x.total_license_cost).vendor if licenses else None
        }
    
    def _generate_quick_recommendations(self, licenses: List[SoftwareLicense], 
                                      usage_data: List[UsageMetric]) -> List[Dict[str, Any]]:
        """Generate quick recommendations"""
        recommendations = []
        
        for license_info in licenses:
            license_usage = [m for m in usage_data if m.license_id == license_info.id]
            if license_usage:
                avg_utilization = sum(m.utilization_percentage for m in license_usage) / len(license_usage)
                if avg_utilization < 30:
                    recommendations.append({
                        "license": license_info.name,
                        "action": "Consider cancellation or downgrade",
                        "potential_savings": license_info.total_license_cost * 0.8
                    })
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _generate_analysis_insights(self, analysis_results: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from analysis results"""
        insights = []
        
        for result in analysis_results:
            analysis = result["analysis"]
            if analysis.get("anomalies"):
                insights.append(f"{result['license']} shows {len(analysis['anomalies'])} usage anomalies")
            
            utilization_stats = analysis.get("utilization_stats", {})
            if utilization_stats.get("mean", 0) < 50:
                insights.append(f"{result['license']} has low average utilization ({utilization_stats['mean']:.1f}%)")
        
        return insights
    
    def _generate_analysis_visualizations(self, analysis_results: List[Dict[str, Any]], 
                                        customization: ReportCustomization) -> List[Dict[str, Any]]:
        """Generate visualizations for analysis report"""
        return [
            {
                "type": "utilization_trends",
                "title": "License Utilization Trends",
                "data": [{"license": r["license"], "utilization": r["analysis"].get("utilization_stats", {}).get("mean", 0)} for r in analysis_results]
            }
        ]
    
    def _generate_recommendation_summary(self, recommendations: List[Dict[str, Any]], 
                                       total_savings: float) -> Dict[str, Any]:
        """Generate summary of recommendations"""
        high_priority = [r for r in recommendations if r["priority"] == "high"]
        
        return {
            "total_recommendations": len(recommendations),
            "high_priority_count": len(high_priority),
            "total_potential_savings": total_savings,
            "top_recommendation": recommendations[0] if recommendations else None
        }
    
    def _summarize_forecasts(self, forecast_data: List[Any]) -> Dict[str, Any]:
        """Summarize forecast data"""
        if not forecast_data:
            return {}
        
        avg_usage = sum(f.predicted_usage for f in forecast_data) / len(forecast_data)
        avg_cost = sum(f.predicted_cost for f in forecast_data) / len(forecast_data)
        avg_confidence = sum(f.confidence_score for f in forecast_data) / len(forecast_data)
        
        return {
            "average_predicted_usage": avg_usage,
            "average_predicted_cost": avg_cost,
            "average_confidence": avg_confidence,
            "trend": forecast_data[0].trend if forecast_data else "stable"
        }
    
    def _analyze_overall_trends(self, forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall forecast trends"""
        if not forecasts:
            return {}
        
        trends = [f["summary"]["trend"] for f in forecasts if f["summary"].get("trend")]
        trend_counts = {}
        for trend in trends:
            trend_counts[trend] = trend_counts.get(trend, 0) + 1
        
        return {
            "dominant_trend": max(trend_counts.items(), key=lambda x: x[1])[0] if trend_counts else "stable",
            "trend_distribution": trend_counts
        }
    
    def _calculate_forecast_confidence(self, forecasts: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate overall forecast confidence"""
        if not forecasts:
            return {"overall_confidence": 0.0}
        
        confidences = [f["summary"]["average_confidence"] for f in forecasts if f["summary"].get("average_confidence")]
        return {
            "overall_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
            "high_confidence_count": len([c for c in confidences if c > 0.8])
        }
    
    def _generate_rankings(self, comparison_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Generate rankings for comparison data"""
        return {
            "by_cost": sorted(comparison_data, key=lambda x: x["cost"], reverse=True),
            "by_utilization": sorted(comparison_data, key=lambda x: x["utilization"], reverse=True),
            "by_efficiency": sorted(comparison_data, key=lambda x: x["efficiency_score"], reverse=True)
        }
    
    def _generate_comparison_insights(self, comparison_data: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from comparison data"""
        insights = []
        
        if len(comparison_data) >= 2:
            most_expensive = max(comparison_data, key=lambda x: x["cost"])
            most_efficient = max(comparison_data, key=lambda x: x["efficiency_score"])
            
            insights.append(f"{most_expensive['license']} is the most expensive at ${most_expensive['cost']:,.0f}")
            insights.append(f"{most_efficient['license']} has the best efficiency score")
        
        return insights

