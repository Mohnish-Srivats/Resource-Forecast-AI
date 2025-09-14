# Adaptive Resource Forecast AI

An AI-powered software license management and cost optimization platform that helps organizations make data-driven decisions about software license renewals, cost optimization, and resource allocation.

# DEMO AND EXPLANATION
https://www.loom.com/share/4519808aac3e45e1b2371a0505905942?sid=327a2d84-8383-4eb9-95fb-adddd643ed19

## Overview

This project is a prototype of an enterprise-grade AI system that was originally developed at internal org for managing software license costs and utilization. The system analyzes historical usage data, predicts future resource needs, and provides intelligent recommendations for license renewals and cost optimization.

## Key Features


### AI-Powered Analysis
- **Cost Forecasting**: Machine learning-based predictions for future spending
- **Intelligent Recommendations**: AI-driven renewal and optimization suggestions

### Comprehensive Reporting
- **AP Team Reports**: Financial analysis, payment schedules, and budget impact
- **Procurement Reports**: Vendor analysis, negotiation opportunities, and market benchmarks
- **Executive Dashboards**: Real-time insights and cost optimization opportunities


## Architecture

```
adaptive-resource-forecast-ai/
├── app/
│   ├── models/           # Data models and schemas
│   ├── services/         # AI agents and business logic
│   ├── api/             # REST API endpoints
│   ├── utils/           # Data management utilities
│   └── main.py          # FastAPI application
├── data/                # Sample data and storage
└── requirements.txt     # Python dependencies
```

## Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **AI/ML**: scikit-learn, pandas, numpy
- **Data Visualization**: Plotly, matplotlib, seaborn
- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS
- **Data Storage**: JSON files (easily extensible to databases)
- **Chat Features**: OpenAI API

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   
   git clone <repository-url>
   cd adaptive-resource-forecast-ai
 

2. **Install dependencies**
   
   pip install -r requirements.txt


3. **Run the application**
   
   python3 run.py
  

4. **Access the application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Usage Guide

### Dashboard Overview
The main dashboard provides:
- **Total Licenses**: Count of active software licenses
- **Total Cost**: Aggregate spending across all licenses
- **Average Utilization**: Overall resource utilization percentage
- **Cost Trends**: Visual representation of spending patterns
- **Recommendations**: AI-generated optimization suggestions

### Key Endpoints

#### License Management
- `GET /api/licenses` - List all licenses
- `GET /api/licenses/{id}` - Get specific license details
- `GET /api/licenses/{id}/usage` - Get usage metrics for a license
- `GET /api/licenses/{id}/forecast` - Get usage/cost forecasts
- `GET /api/licenses/{id}/recommendation` - Get renewal recommendations

#### Reports
- `GET /api/reports/license-summary` - Comprehensive license report
- `GET /api/reports/ap-team` - AP team financial report
- `GET /api/reports/procurement` - Procurement team report

### Sample Data
The system comes pre-loaded with sample data including:
- **Workato Integration Platform** (per-task billing)
- **Slack Business+** (per-user billing)
- **AWS Enterprise Support** (tiered billing)
- **Salesforce Enterprise** (per-user billing)
- **Zoom Pro** (per-user billing)
- **Jira Software** (per-user billing)

## AI Features Explained

### Forecasting Agent
- **Time Series Analysis**: Predicts future usage based on historical data
- **Cost Projection**: Estimates future costs based on billing models
- **Confidence Scoring**: Provides confidence levels for predictions
- **Trend Analysis**: Determines upward, downward, or stable trends

### Recommendation Engine
- **Multi-Factor Analysis**: Considers utilization, cost trends, and forecasts
- **Risk Assessment**: Identifies potential risks and mitigation strategies
- **Alternative Suggestions**: Proposes alternative licensing options
- **Priority Scoring**: Ranks recommendations by importance and impact

## Sample Scenarios

### Scenario 1: Low Utilization License
- **License**: Jira Software (400/1200 users = 33% utilization)
- **Recommendation**: Downgrade to smaller tier
- **Potential Savings**: $4,650 annually
- **Risk Factors**: None identified

### Scenario 2: High Utilization License
- **License**: Zoom Pro (1200/1200 users = 100% utilization)
- **Recommendation**: Negotiate for better rates or upgrade
- **Potential Savings**: $2,700 through negotiation
- **Risk Factors**: Service degradation risk



### Scenario 3: Task-Based License
- **License**: Workato (750,000/1,000,000 tasks = 75% utilization)
- **Recommendation**: Renew with monitoring
- **Potential Savings**: $0 (optimal utilization)
- **Risk Factors**: Usage growth trend detected


**Note**: This is a prototype demonstration of the original system. Some features may be simplified for educational purposes.
