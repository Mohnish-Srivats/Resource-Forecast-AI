from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
import json

from ..models.license_models import (
    SoftwareLicense, UsageMetric, Recommendation, 
    LicenseReport, APTeamReport, ProcurementReport
)
from ..services.ai_agent import RecommendationEngine, LicenseUtilizationAnalyzer, LicenseForecastingAgent
from ..utils.data_manager import DataManager

router = APIRouter()

# Initialize services
recommendation_engine = RecommendationEngine()
utilization_analyzer = LicenseUtilizationAnalyzer()
forecasting_agent = LicenseForecastingAgent()
data_manager = DataManager()


@router.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard for the Adaptive Resource Forecast AI"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Adaptive Resource Forecast AI</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto px-4 py-8">
            <header class="mb-8">
                <div class="flex justify-between items-center">
                    <div>
                        <h1 class="text-4xl font-bold text-gray-800 mb-2">Adaptive Resource Forecast AI</h1>
                        <p class="text-gray-600">Intelligent License Management & Cost Optimization</p>
                    </div>
                    <div class="flex space-x-3">
                        <a href="/chat" class="bg-gradient-to-r from-purple-500 to-blue-500 text-white px-6 py-3 rounded-lg hover:from-purple-600 hover:to-blue-600 transition-colors">
                            🤖 AI License Assistant
                        </a>
                    </div>
                </div>
            </header>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">Total Licenses</h3>
                    <p class="text-3xl font-bold text-blue-600" id="total-licenses">-</p>
                </div>
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">Total Cost</h3>
                    <p class="text-3xl font-bold text-green-600" id="total-cost">-</p>
                </div>
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">Avg Utilization</h3>
                    <p class="text-3xl font-bold text-orange-600" id="avg-utilization">-</p>
                </div>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">Cost Trend</h3>
                    <div id="cost-trend-chart"></div>
                </div>
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">Utilization Distribution</h3>
                    <div id="utilization-chart"></div>
                </div>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow-md mb-8">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">License Recommendations</h3>
                <div id="recommendations-table"></div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">AP Team Report</h3>
                    <button onclick="generateAPReport()" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                        Generate AP Report
                    </button>
                    <div id="ap-report" class="mt-4"></div>
                </div>
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">Procurement Report</h3>
                    <button onclick="generateProcurementReport()" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                        Generate Procurement Report
                    </button>
                    <div id="procurement-report" class="mt-4"></div>
                </div>
            </div>
        </div>
        
        <script>
            // Load dashboard data
            async function loadDashboard() {
                try {
                    const response = await fetch('/api/dashboard-summary');
                    const data = await response.json();
                    
                    document.getElementById('total-licenses').textContent = data.total_licenses;
                    document.getElementById('total-cost').textContent = '$' + data.total_cost.toLocaleString();
                    document.getElementById('avg-utilization').textContent = data.avg_utilization.toFixed(1) + '%';
                    
                    // Load charts
                    loadCostTrendChart(data.cost_trend);
                    loadUtilizationChart(data.utilization_distribution);
                    loadRecommendationsTable(data.recommendations);
                } catch (error) {
                    console.error('Error loading dashboard:', error);
                }
            }
            
            function loadCostTrendChart(data) {
                const trace = {
                    x: data.dates,
                    y: data.costs,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Cost Trend',
                    line: { color: '#3B82F6' }
                };
                
                const layout = {
                    title: '',
                    xaxis: { title: 'Date' },
                    yaxis: { title: 'Cost ($)' },
                    margin: { t: 30, b: 40, l: 40, r: 20 }
                };
                
                Plotly.newPlot('cost-trend-chart', [trace], layout, {responsive: true});
            }
            
            function loadUtilizationChart(data) {
                const trace = {
                    x: data.ranges,
                    y: data.counts,
                    type: 'bar',
                    name: 'License Count',
                    marker: { color: '#F59E0B' }
                };
                
                const layout = {
                    title: '',
                    xaxis: { title: 'Utilization Range (%)' },
                    yaxis: { title: 'Number of Licenses' },
                    margin: { t: 30, b: 40, l: 40, r: 20 }
                };
                
                Plotly.newPlot('utilization-chart', [trace], layout, {responsive: true});
            }
            
            function loadRecommendationsTable(recommendations) {
                const table = document.getElementById('recommendations-table');
                let html = '<table class="min-w-full divide-y divide-gray-200"><thead class="bg-gray-50"><tr>';
                html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">License</th>';
                html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Recommendation</th>';
                html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>';
                html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Savings</th>';
                html += '<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th></tr></thead><tbody>';
                
                recommendations.forEach(rec => {
                    const priorityColor = rec.priority === 'high' ? 'text-red-600' : 
                                        rec.priority === 'medium' ? 'text-yellow-600' : 'text-green-600';
                    html += `<tr class="bg-white"><td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${rec.license_name}</td>`;
                    html += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${rec.recommendation}</td>`;
                    html += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${(rec.confidence * 100).toFixed(1)}%</td>`;
                    html += `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">$${rec.estimated_savings.toLocaleString()}</td>`;
                    html += `<td class="px-6 py-4 whitespace-nowrap text-sm ${priorityColor}">${rec.priority}</td></tr>`;
                });
                
                html += '</tbody></table>';
                table.innerHTML = html;
            }
            
            async function generateAPReport() {
                try {
                    const response = await fetch('/api/reports/ap-team');
                    const data = await response.json();
                    displayAPReport(data);
                } catch (error) {
                    console.error('Error generating AP report:', error);
                }
            }
            
            async function generateProcurementReport() {
                try {
                    const response = await fetch('/api/reports/procurement');
                    const data = await response.json();
                    displayProcurementReport(data);
                } catch (error) {
                    console.error('Error generating procurement report:', error);
                }
            }
            
            function displayAPReport(data) {
                const reportDiv = document.getElementById('ap-report');
                let html = '<div class="space-y-4">';
                html += `<h4 class="font-semibold">Upcoming Renewals: ${data.upcoming_renewals.length}</h4>`;
                html += `<h4 class="font-semibold">Total Budget Impact: $${data.budget_impact.total.toLocaleString()}</h4>`;
                html += '<h4 class="font-semibold">Cost Optimization Opportunities:</h4>';
                data.cost_optimization_opportunities.forEach(opp => {
                    html += `<div class="p-3 bg-blue-50 rounded"><strong>${opp.license_name}:</strong> $${opp.potential_savings.toLocaleString()}</div>`;
                });
                html += '</div>';
                reportDiv.innerHTML = html;
            }
            
            function displayProcurementReport(data) {
                const reportDiv = document.getElementById('procurement-report');
                let html = '<div class="space-y-4">';
                html += '<h4 class="font-semibold">Vendor Analysis:</h4>';
                Object.entries(data.vendor_analysis).forEach(([vendor, info]) => {
                    html += `<div class="p-3 bg-green-50 rounded"><strong>${vendor}:</strong> ${info.total_cost} licenses, $${info.total_cost.toLocaleString()}</div>`;
                });
                html += '<h4 class="font-semibold">Negotiation Opportunities:</h4>';
                data.contract_negotiation_opportunities.forEach(opp => {
                    html += `<div class="p-3 bg-yellow-50 rounded"><strong>${opp.license_name}:</strong> ${opp.opportunity}</div>`;
                });
                html += '</div>';
                reportDiv.innerHTML = html;
            }
            
            // Load dashboard on page load
            loadDashboard();
        </script>
    </body>
    </html>
    """


@router.get("/api/dashboard-summary")
async def get_dashboard_summary():
    """Get summary data for dashboard"""
    try:
        licenses = data_manager.get_all_licenses()
        usage_data = data_manager.get_all_usage_metrics()
        
        # Calculate summary metrics
        total_licenses = len(licenses)
        total_cost = sum(license.total_license_cost for license in licenses)
        
        # Calculate average utilization
        if usage_data:
            avg_utilization = sum(metric.utilization_percentage for metric in usage_data) / len(usage_data)
        else:
            avg_utilization = 0
        
        # Generate cost trend data (last 30 days)
        cost_trend = data_manager.get_cost_trend_data(30)
        
        # Generate utilization distribution
        utilization_distribution = data_manager.get_utilization_distribution()
        
        # Get recommendations
        recommendations = []
        for license_info in licenses:
            license_usage = [metric for metric in usage_data if metric.license_id == license_info.id]
            if license_usage:
                rec = recommendation_engine.generate_recommendations(license_info, license_usage)
                recommendations.append({
                    "license_name": license_info.name,
                    "recommendation": rec.recommendation,
                    "confidence": rec.confidence,
                    "estimated_savings": rec.estimated_savings or 0,
                    "priority": rec.priority
                })
        
        return {
            "total_licenses": total_licenses,
            "total_cost": total_cost,
            "avg_utilization": avg_utilization,
            "cost_trend": cost_trend,
            "utilization_distribution": utilization_distribution,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/licenses")
async def get_licenses():
    """Get all software licenses"""
    return data_manager.get_all_licenses()


@router.get("/api/licenses/{license_id}")
async def get_license(license_id: str):
    """Get specific license details"""
    license_info = data_manager.get_license(license_id)
    if not license_info:
        raise HTTPException(status_code=404, detail="License not found")
    return license_info


@router.get("/api/licenses/{license_id}/usage")
async def get_license_usage(license_id: str):
    """Get usage metrics for a specific license"""
    return data_manager.get_usage_metrics(license_id)


@router.get("/api/licenses/{license_id}/forecast")
async def get_license_forecast(license_id: str, days: int = 90):
    """Get forecast for a specific license"""
    license_info = data_manager.get_license(license_id)
    if not license_info:
        raise HTTPException(status_code=404, detail="License not found")
    
    usage_data = data_manager.get_usage_metrics(license_id)
    if not usage_data:
        raise HTTPException(status_code=404, detail="No usage data found")
    
    forecasts = forecasting_agent.generate_forecast(usage_data, license_info, days)
    return forecasts


@router.get("/api/licenses/{license_id}/recommendation")
async def get_license_recommendation(license_id: str):
    """Get recommendation for a specific license"""
    license_info = data_manager.get_license(license_id)
    if not license_info:
        raise HTTPException(status_code=404, detail="License not found")
    
    usage_data = data_manager.get_usage_metrics(license_id)
    if not usage_data:
        raise HTTPException(status_code=404, detail="No usage data found")
    
    recommendation = recommendation_engine.generate_recommendations(license_info, usage_data)
    return recommendation


@router.get("/api/reports/license-summary")
async def get_license_summary_report():
    """Generate comprehensive license summary report"""
    try:
        licenses = data_manager.get_all_licenses()
        usage_data = data_manager.get_all_usage_metrics()
        
        recommendations = []
        for license_info in licenses:
            license_usage = [metric for metric in usage_data if metric.license_id == license_info.id]
            if license_usage:
                rec = recommendation_engine.generate_recommendations(license_info, license_usage)
                recommendations.append(rec)
        
        # Calculate cost breakdown
        cost_breakdown = {}
        for license_info in licenses:
            vendor = license_info.vendor
            if vendor not in cost_breakdown:
                cost_breakdown[vendor] = 0
            cost_breakdown[vendor] += license_info.total_license_cost
        
        # Calculate utilization summary
        utilization_summary = {
            "high_utilization": len([l for l in licenses if l.current_units and l.max_units and (l.current_units / l.max_units) > 0.8]),
            "low_utilization": len([l for l in licenses if l.current_units and l.max_units and (l.current_units / l.max_units) < 0.3]),
            "medium_utilization": len(licenses) - len([l for l in licenses if l.current_units and l.max_units and (l.current_units / l.max_units) > 0.8]) - len([l for l in licenses if l.current_units and l.max_units and (l.current_units / l.max_units) < 0.3])
        }
        
        report = LicenseReport(
            report_id=f"LSR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            generated_date=datetime.now(),
            period_start=date.today() - timedelta(days=365),
            period_end=date.today(),
            total_licenses=len(licenses),
            total_cost=sum(license.total_license_cost for license in licenses),
            total_utilization=sum(metric.utilization_percentage for metric in usage_data) / len(usage_data) if usage_data else 0,
            recommendations=recommendations,
            cost_breakdown=cost_breakdown,
            utilization_summary=utilization_summary,
            forecast_summary={"total_forecasts": len(recommendations)}
        )
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/reports/ap-team")
async def get_ap_team_report():
    """Generate AP team report"""
    try:
        licenses = data_manager.get_all_licenses()
        usage_data = data_manager.get_all_usage_metrics()
        
        # Find upcoming renewals (next 90 days)
        upcoming_renewals = []
        for license_info in licenses:
            days_to_expiry = (license_info.end_date - date.today()).days
            if 0 <= days_to_expiry <= 90:
                upcoming_renewals.append({
                    "license_name": license_info.name,
                    "vendor": license_info.vendor,
                    "expiry_date": license_info.end_date.isoformat(),
                    "days_to_expiry": days_to_expiry,
                    "cost": license_info.total_license_cost
                })
        
        # Calculate cost analysis
        total_annual_cost = sum(license.total_license_cost * (12 / license.license_period_months) for license in licenses)
        monthly_cost = total_annual_cost / 12
        
        # Budget impact analysis
        budget_impact = {
            "total": total_annual_cost,
            "monthly": monthly_cost,
            "quarterly": monthly_cost * 3
        }
        
        # Payment schedule
        payment_schedule = []
        for license_info in licenses:
            if license_info.auto_renewal:
                payment_schedule.append({
                    "license_name": license_info.name,
                    "next_payment_date": license_info.end_date.isoformat(),
                    "amount": license_info.total_license_cost
                })
        
        # Cost optimization opportunities
        cost_optimization_opportunities = []
        for license_info in licenses:
            license_usage = [metric for metric in usage_data if metric.license_id == license_info.id]
            if license_usage:
                rec = recommendation_engine.generate_recommendations(license_info, license_usage)
                if rec.estimated_savings and rec.estimated_savings > 0:
                    cost_optimization_opportunities.append({
                        "license_name": license_info.name,
                        "potential_savings": rec.estimated_savings,
                        "recommendation": rec.recommendation
                    })
        
        report = APTeamReport(
            report_id=f"APR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            generated_date=datetime.now(),
            upcoming_renewals=upcoming_renewals,
            cost_analysis={"total_annual": total_annual_cost, "monthly": monthly_cost},
            budget_impact=budget_impact,
            payment_schedule=payment_schedule,
            cost_optimization_opportunities=cost_optimization_opportunities
        )
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/reports/procurement")
async def get_procurement_report():
    """Generate procurement team report"""
    try:
        licenses = data_manager.get_all_licenses()
        usage_data = data_manager.get_all_usage_metrics()
        
        # Vendor analysis
        vendor_analysis = {}
        for license_info in licenses:
            vendor = license_info.vendor
            if vendor not in vendor_analysis:
                vendor_analysis[vendor] = {
                    "license_count": 0,
                    "total_cost": 0,
                    "licenses": []
                }
            vendor_analysis[vendor]["license_count"] += 1
            vendor_analysis[vendor]["total_cost"] += license_info.total_license_cost
            vendor_analysis[vendor]["licenses"].append(license_info.name)
        
        # Contract negotiation opportunities
        contract_negotiation_opportunities = []
        for license_info in licenses:
            license_usage = [metric for metric in usage_data if metric.license_id == license_info.id]
            if license_usage:
                rec = recommendation_engine.generate_recommendations(license_info, license_usage)
                if rec.recommendation in ["negotiate", "downgrade"]:
                    contract_negotiation_opportunities.append({
                        "license_name": license_info.name,
                        "vendor": license_info.vendor,
                        "opportunity": f"Negotiate for {rec.recommendation}",
                        "potential_savings": rec.estimated_savings or 0
                    })
        
        # Market benchmarks (simplified)
        market_benchmarks = {
            "average_license_cost": sum(license.total_license_cost for license in licenses) / len(licenses) if licenses else 0,
            "most_expensive_vendor": max(vendor_analysis.items(), key=lambda x: x[1]["total_cost"])[0] if vendor_analysis else None,
            "total_vendors": len(vendor_analysis)
        }
        
        # Supplier performance
        supplier_performance = {}
        for vendor, data in vendor_analysis.items():
            supplier_performance[vendor] = {
                "total_spend": data["total_cost"],
                "license_count": data["license_count"],
                "average_license_cost": data["total_cost"] / data["license_count"]
            }
        
        # Cost reduction recommendations
        cost_reduction_recommendations = []
        for license_info in licenses:
            license_usage = [metric for metric in usage_data if metric.license_id == license_info.id]
            if license_usage:
                rec = recommendation_engine.generate_recommendations(license_info, license_usage)
                if rec.estimated_savings and rec.estimated_savings > 1000:
                    cost_reduction_recommendations.append({
                        "license_name": license_info.name,
                        "vendor": license_info.vendor,
                        "recommendation": rec.recommendation,
                        "potential_savings": rec.estimated_savings,
                        "priority": rec.priority
                    })
        
        report = ProcurementReport(
            report_id=f"PR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            generated_date=datetime.now(),
            vendor_analysis=vendor_analysis,
            contract_negotiation_opportunities=contract_negotiation_opportunities,
            market_benchmarks=market_benchmarks,
            supplier_performance=supplier_performance,
            cost_reduction_recommendations=cost_reduction_recommendations
        )
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
