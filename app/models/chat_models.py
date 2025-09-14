from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum



class IntentCategory(str, Enum):
    """Categories of user intents"""
    DASHBOARD = "dashboard"
    REPORT = "report"
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"
    FORECAST = "forecast"
    COMPARISON = "comparison"
    OPTIMIZATION = "optimization"
    GREETING = "greeting"
    HELP = "help"
    UNKNOWN = "unknown"


class IntentAction(str, Enum):
    """Actions within intents"""
    SHOW = "show"
    GENERATE = "generate"
    COMPARE = "compare"
    ANALYZE = "analyze"
    RECOMMEND = "recommend"
    FORECAST = "forecast"
    OPTIMIZE = "optimize"
    EXPLAIN = "explain"
    GREET = "greet"
    HELP = "help"


class ChatMessage(BaseModel):
    """Model for chat messages"""
    id: str
    user_id: str
    message: str
    timestamp: datetime
    intent: Optional[IntentCategory] = None
    action: Optional[IntentAction] = None
    entities: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Model for chat responses"""
    message: str
    data: Optional[Dict[str, Any]] = None
    report: Optional[Dict[str, Any]] = None
    visualizations: Optional[List[Dict[str, Any]]] = None
    suggestions: Optional[List[str]] = None
    follow_up_questions: Optional[List[str]] = None
    confidence: float = Field(ge=0, le=1, default=0.8)
    response_type: str = Field(default="text")  # text, report, visualization, mixed


class Intent(BaseModel):
    """Model for parsed user intent"""
    category: IntentCategory
    action: IntentAction
    entities: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0, le=1, default=0.8)
    original_message: str


class ConversationContext(BaseModel):
    """Model for conversation context"""
    user_id: str
    session_id: str
    current_topic: Optional[str] = None
    previous_intents: List[IntentCategory] = Field(default_factory=list)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    last_report_type: Optional[str] = None
    last_analysis_focus: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Model for chat API requests"""
    message: str
    user_id: str = "default_user"
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatHistory(BaseModel):
    """Model for chat history"""
    session_id: str
    user_id: str
    messages: List[ChatMessage] = Field(default_factory=list)
    responses: List[ChatResponse] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CustomReportRequest(BaseModel):
    """Model for custom report generation requests"""
    report_type: str
    parameters: Dict[str, Any]
    format: str = "json"  # json, html, pdf
    include_visualizations: bool = True
    custom_filters: Optional[Dict[str, Any]] = None


class ReportCustomization(BaseModel):
    """Model for report customization options"""
    time_period: Optional[str] = None
    license_filters: Optional[List[str]] = None
    metric_focus: Optional[List[str]] = None
    team_perspective: Optional[str] = None  # ap, procurement, executive, technical
    detail_level: str = "standard"  # summary, standard, detailed
    include_forecasts: bool = True
    include_recommendations: bool = True
    include_visualizations: bool = True

