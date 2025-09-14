from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


class BillingType(str, Enum):
    """Types of billing models for software licenses"""
    PER_USER = "per_user"
    PER_TASK = "per_task"
    PER_STORAGE = "per_storage"
    PER_API_CALL = "per_api_call"
    FLAT_RATE = "flat_rate"
    TIERED = "tiered"


class LicenseStatus(str, Enum):
    """Status of software licenses"""
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING_RENEWAL = "pending_renewal"
    CANCELLED = "cancelled"


class SoftwareLicense(BaseModel):
    """Model representing a software license"""
    id: str
    name: str
    vendor: str
    billing_type: BillingType
    cost_per_unit: float = Field(description="Cost per unit (user, task, storage, etc.)")
    total_license_cost: float = Field(description="Total cost of the license")
    license_period_months: int = Field(description="License period in months")
    start_date: date
    end_date: date
    status: LicenseStatus
    max_units: Optional[int] = Field(description="Maximum units allowed (users, tasks, etc.)")
    current_units: Optional[int] = Field(description="Current units in use")
    auto_renewal: bool = False
    contract_details: Optional[Dict[str, Any]] = None


class UsageMetric(BaseModel):
    """Model representing usage metrics for a software license"""
    id: str
    license_id: str
    date: date
    units_used: float = Field(description="Number of units used (tasks, API calls, etc.)")
    cost_incurred: float = Field(description="Cost incurred for this usage")
    utilization_percentage: float = Field(description="Percentage of license utilized")
    peak_usage: Optional[float] = None
    average_usage: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class ForecastData(BaseModel):
    """Model for forecasting data"""
    license_id: str
    forecast_date: date
    predicted_usage: float
    predicted_cost: float
    confidence_score: float = Field(ge=0, le=1)
    trend: str = Field(description="upward, downward, stable")
    seasonal_factors: Optional[Dict[str, float]] = None


class Recommendation(BaseModel):
    """Model for license renewal recommendations"""
    license_id: str
    recommendation: str = Field(description="renew, cancel, negotiate, downgrade")
    confidence: float = Field(ge=0, le=1)
    reasoning: List[str] = Field(description="List of reasons for the recommendation")
    estimated_savings: Optional[float] = None
    risk_factors: List[str] = []
    alternative_options: Optional[List[Dict[str, Any]]] = None
    priority: str = Field(description="high, medium, low")


class LicenseReport(BaseModel):
    """Model for comprehensive license reports"""
    report_id: str
    generated_date: datetime
    period_start: date
    period_end: date
    total_licenses: int
    total_cost: float
    total_utilization: float
    recommendations: List[Recommendation]
    cost_breakdown: Dict[str, float]
    utilization_summary: Dict[str, Any]
    forecast_summary: Dict[str, Any]


class APTeamReport(BaseModel):
    """Specialized report for AP team"""
    report_id: str
    generated_date: datetime
    upcoming_renewals: List[Dict[str, Any]]
    cost_analysis: Dict[str, float]
    budget_impact: Dict[str, float]
    payment_schedule: List[Dict[str, Any]]
    cost_optimization_opportunities: List[Dict[str, Any]]


class ProcurementReport(BaseModel):
    """Specialized report for procurement team"""
    report_id: str
    generated_date: datetime
    vendor_analysis: Dict[str, Any]
    contract_negotiation_opportunities: List[Dict[str, Any]]
    market_benchmarks: Dict[str, Any]
    supplier_performance: Dict[str, Any]
    cost_reduction_recommendations: List[Dict[str, Any]]
