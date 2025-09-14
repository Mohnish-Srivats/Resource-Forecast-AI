import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import random

from ..models.license_models import SoftwareLicense, UsageMetric, BillingType, LicenseStatus


class DataManager:
    """Manages data operations for the Adaptive Resource Forecast AI"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.licenses_file = os.path.join(data_dir, "licenses.json")
        self.usage_file = os.path.join(data_dir, "usage_metrics.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize with sample data if files don't exist
        if not os.path.exists(self.licenses_file):
            self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample data for demonstration"""
        # Sample licenses
        sample_licenses = [
            {
                "id": "workato_001",
                "name": "Workato Integration Platform",
                "vendor": "Workato",
                "billing_type": "per_task",
                "cost_per_unit": 0.15,
                "total_license_cost": 50000,
                "license_period_months": 12,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "status": "active",
                "max_units": 1000000,
                "current_units": 750000,
                "auto_renewal": True,
                "contract_details": {"tier": "enterprise", "support_level": "premium"}
            },
            {
                "id": "slack_001",
                "name": "Slack Business+",
                "vendor": "Slack",
                "billing_type": "per_user",
                "cost_per_unit": 12.50,
                "total_license_cost": 15000,
                "license_period_months": 12,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "status": "active",
                "max_units": 1200,
                "current_units": 950,
                "auto_renewal": True,
                "contract_details": {"plan": "business_plus", "features": ["sso", "compliance"]}
            },
            {
                "id": "aws_001",
                "name": "AWS Enterprise Support",
                "vendor": "Amazon Web Services",
                "billing_type": "tiered",
                "cost_per_unit": 0.0,
                "total_license_cost": 25000,
                "license_period_months": 12,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "status": "active",
                "max_units": None,
                "current_units": None,
                "auto_renewal": True,
                "contract_details": {"support_level": "enterprise", "response_time": "15_minutes"}
            },
            {
                "id": "salesforce_001",
                "name": "Salesforce Enterprise",
                "vendor": "Salesforce",
                "billing_type": "per_user",
                "cost_per_unit": 150.00,
                "total_license_cost": 180000,
                "license_period_months": 12,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "status": "active",
                "max_units": 1200,
                "current_units": 800,
                "auto_renewal": True,
                "contract_details": {"edition": "enterprise", "add_ons": ["marketing_cloud"]}
            },
            {
                "id": "zoom_001",
                "name": "Zoom Pro",
                "vendor": "Zoom",
                "billing_type": "per_user",
                "cost_per_unit": 14.99,
                "total_license_cost": 18000,
                "license_period_months": 12,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "status": "active",
                "max_units": 1200,
                "current_units": 1200,
                "auto_renewal": True,
                "contract_details": {"plan": "pro", "features": ["recording", "webinar"]}
            },
            {
                "id": "jira_001",
                "name": "Jira Software",
                "vendor": "Atlassian",
                "billing_type": "per_user",
                "cost_per_unit": 7.75,
                "total_license_cost": 9300,
                "license_period_months": 12,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "status": "active",
                "max_units": 1200,
                "current_units": 400,
                "auto_renewal": True,
                "contract_details": {"deployment": "cloud", "add_ons": ["confluence"]}
            }
        ]
        
        # Convert to SoftwareLicense objects
        licenses = []
        for license_data in sample_licenses:
            license_data["start_date"] = datetime.strptime(license_data["start_date"], "%Y-%m-%d").date()
            license_data["end_date"] = datetime.strptime(license_data["end_date"], "%Y-%m-%d").date()
            licenses.append(SoftwareLicense(**license_data))
        
        self._save_licenses(licenses)
        
        # Generate sample usage data
        self._generate_sample_usage_data(licenses)
    
    def _generate_sample_usage_data(self, licenses: List[SoftwareLicense]):
        """Generate sample usage data for demonstration"""
        usage_metrics = []
        
        for license_info in licenses:
            # Generate 90 days of usage data
            start_date = date.today() - timedelta(days=90)
            
            for i in range(90):
                current_date = start_date + timedelta(days=i)
                
                # Generate realistic usage patterns
                if license_info.billing_type == "per_task":
                    # Workato-like task usage with some seasonality
                    base_usage = 8000
                    seasonal_factor = 1 + 0.3 * (i % 7 == 0)  # Higher on Mondays
                    weekly_trend = 1 + 0.1 * (i / 7)  # Slight upward trend
                    noise = random.uniform(0.8, 1.2)
                    units_used = int(base_usage * seasonal_factor * weekly_trend * noise)
                    
                elif license_info.billing_type == "per_user":
                    # User-based licenses (more stable)
                    base_usage = license_info.current_units or 500
                    noise = random.uniform(0.95, 1.05)
                    units_used = int(base_usage * noise)
                    
                else:
                    # Flat rate or tiered
                    units_used = 1
                
                # Calculate utilization percentage
                if license_info.max_units:
                    utilization_percentage = (units_used / license_info.max_units) * 100
                else:
                    utilization_percentage = random.uniform(20, 80)
                
                # Calculate cost incurred
                if license_info.billing_type == "per_task":
                    cost_incurred = units_used * license_info.cost_per_unit
                elif license_info.billing_type == "per_user":
                    cost_incurred = (license_info.total_license_cost / 365)  # Daily cost
                else:
                    cost_incurred = (license_info.total_license_cost / 365)  # Daily cost
                
                usage_metric = UsageMetric(
                    id=f"{license_info.id}_usage_{i}",
                    license_id=license_info.id,
                    date=current_date,
                    units_used=units_used,
                    cost_incurred=cost_incurred,
                    utilization_percentage=utilization_percentage,
                    peak_usage=units_used * 1.2,
                    average_usage=units_used * 0.9,
                    metadata={"generated": True}
                )
                usage_metrics.append(usage_metric)
        
        self._save_usage_metrics(usage_metrics)
    
    def _save_licenses(self, licenses: List[SoftwareLicense]):
        """Save licenses to file"""
        licenses_data = []
        for license_info in licenses:
            license_dict = license_info.model_dump()
            license_dict["start_date"] = license_dict["start_date"].isoformat()
            license_dict["end_date"] = license_dict["end_date"].isoformat()
            licenses_data.append(license_dict)
        
        with open(self.licenses_file, 'w') as f:
            json.dump(licenses_data, f, indent=2)
    
    def _save_usage_metrics(self, usage_metrics: List[UsageMetric]):
        """Save usage metrics to file"""
        usage_data = []
        for metric in usage_metrics:
            metric_dict = metric.model_dump()
            metric_dict["date"] = metric_dict["date"].isoformat()
            usage_data.append(metric_dict)
        
        with open(self.usage_file, 'w') as f:
            json.dump(usage_data, f, indent=2)
    
    def get_all_licenses(self) -> List[SoftwareLicense]:
        """Get all software licenses"""
        if not os.path.exists(self.licenses_file):
            return []
        
        with open(self.licenses_file, 'r') as f:
            licenses_data = json.load(f)
        
        licenses = []
        for license_data in licenses_data:
            license_data["start_date"] = datetime.strptime(license_data["start_date"], "%Y-%m-%d").date()
            license_data["end_date"] = datetime.strptime(license_data["end_date"], "%Y-%m-%d").date()
            licenses.append(SoftwareLicense(**license_data))
        
        return licenses
    
    def get_license(self, license_id: str) -> Optional[SoftwareLicense]:
        """Get specific license by ID"""
        licenses = self.get_all_licenses()
        for license_info in licenses:
            if license_info.id == license_id:
                return license_info
        return None
    
    def get_all_usage_metrics(self) -> List[UsageMetric]:
        """Get all usage metrics"""
        if not os.path.exists(self.usage_file):
            return []
        
        with open(self.usage_file, 'r') as f:
            usage_data = json.load(f)
        
        metrics = []
        for metric_data in usage_data:
            metric_data["date"] = datetime.strptime(metric_data["date"], "%Y-%m-%d").date()
            metrics.append(UsageMetric(**metric_data))
        
        return metrics
    
    def get_usage_metrics(self, license_id: str) -> List[UsageMetric]:
        """Get usage metrics for specific license"""
        all_metrics = self.get_all_usage_metrics()
        return [metric for metric in all_metrics if metric.license_id == license_id]
    
    def get_cost_trend_data(self, days: int = 30) -> Dict[str, Any]:
        """Get cost trend data for the last N days"""
        usage_metrics = self.get_all_usage_metrics()
        
        # Filter last N days
        cutoff_date = date.today() - timedelta(days=days)
        recent_metrics = [m for m in usage_metrics if m.date >= cutoff_date]
        
        # Group by date and sum costs
        daily_costs = {}
        for metric in recent_metrics:
            date_str = metric.date.isoformat()
            if date_str not in daily_costs:
                daily_costs[date_str] = 0
            daily_costs[date_str] += metric.cost_incurred
        
        # Sort by date
        sorted_dates = sorted(daily_costs.keys())
        costs = [daily_costs[date_str] for date_str in sorted_dates]
        
        return {
            "dates": sorted_dates,
            "costs": costs
        }
    
    def get_utilization_distribution(self) -> Dict[str, Any]:
        """Get utilization distribution across all licenses"""
        usage_metrics = self.get_all_usage_metrics()
        
        if not usage_metrics:
            return {"ranges": [], "counts": []}
        
        # Get recent utilization data (last 30 days)
        cutoff_date = date.today() - timedelta(days=30)
        recent_metrics = [m for m in usage_metrics if m.date >= cutoff_date]
        
        # Group by license and get average utilization
        license_utilization = {}
        for metric in recent_metrics:
            if metric.license_id not in license_utilization:
                license_utilization[metric.license_id] = []
            license_utilization[metric.license_id].append(metric.utilization_percentage)
        
        # Calculate average utilization per license
        avg_utilizations = []
        for license_id, utilizations in license_utilization.items():
            avg_utilizations.append(sum(utilizations) / len(utilizations))
        
        # Create distribution ranges
        ranges = ["0-20%", "21-40%", "41-60%", "61-80%", "81-100%"]
        counts = [0, 0, 0, 0, 0]
        
        for avg_util in avg_utilizations:
            if avg_util <= 20:
                counts[0] += 1
            elif avg_util <= 40:
                counts[1] += 1
            elif avg_util <= 60:
                counts[2] += 1
            elif avg_util <= 80:
                counts[3] += 1
            else:
                counts[4] += 1
        
        return {
            "ranges": ranges,
            "counts": counts
        }
    
    def add_license(self, license_info: SoftwareLicense):
        """Add new license"""
        licenses = self.get_all_licenses()
        licenses.append(license_info)
        self._save_licenses(licenses)
    
    def update_license(self, license_id: str, updated_license: SoftwareLicense):
        """Update existing license"""
        licenses = self.get_all_licenses()
        for i, license_info in enumerate(licenses):
            if license_info.id == license_id:
                licenses[i] = updated_license
                self._save_licenses(licenses)
                return True
        return False
    
    def delete_license(self, license_id: str):
        """Delete license"""
        licenses = self.get_all_licenses()
        licenses = [l for l in licenses if l.id != license_id]
        self._save_licenses(licenses)
        
        # Also delete associated usage metrics
        usage_metrics = self.get_all_usage_metrics()
        usage_metrics = [m for m in usage_metrics if m.license_id != license_id]
        self._save_usage_metrics(usage_metrics)
