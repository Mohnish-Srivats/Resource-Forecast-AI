import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from ..models.chat_models import ChatMessage, Intent, IntentCategory, IntentAction


class OpenAIModel(str, Enum):
    """Available OpenAI models"""
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"


class GenAIService:
    """Service for OpenAI integration only"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = OpenAIModel.GPT4_TURBO
        
        # Model capabilities mapping
        self.model_capabilities = {
            OpenAIModel.GPT4_TURBO: {
                "reasoning": "excellent",
                "speed": "medium",
                "cost": "high",
                "context_length": 128000,
                "best_for": ["complex_analysis", "reasoning", "detailed_reports"]
            },
            OpenAIModel.GPT4: {
                "reasoning": "excellent",
                "speed": "medium",
                "cost": "high",
                "context_length": 8192,
                "best_for": ["complex_analysis", "reasoning"]
            },
            OpenAIModel.GPT35_TURBO: {
                "reasoning": "good",
                "speed": "fast",
                "cost": "medium",
                "context_length": 16384,
                "best_for": ["general_chat", "simple_analysis", "quick_responses"]
            }
        }
    
    async def process_with_genai(self, 
                               message: str, 
                               context: Dict[str, Any],
                               task_type: str = "general",
                               preferred_model: Optional[OpenAIModel] = None) -> Dict[str, Any]:
        """Process message with OpenAI model"""
        
        if not self.openai_api_key:
            return {
                "response": "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.",
                "model_used": None,
                "success": False,
                "error": "No API key"
            }
        
        # Select best model for the task
        model = self._select_best_model(task_type, preferred_model)
        
        try:
            response = await self._call_openai_model(model, message, context, task_type)
            return {
                "response": response,
                "model_used": model,
                "success": True
            }
        except Exception as e:
            return {
                "response": f"I'm sorry, I encountered an error processing your request: {str(e)}",
                "model_used": model,
                "success": False,
                "error": str(e)
            }
    
    def _select_best_model(self, task_type: str, preferred_model: Optional[OpenAIModel]) -> OpenAIModel:
        """Select the best OpenAI model for the given task type"""
        
        if preferred_model:
            return preferred_model
        
        # Task-specific model selection
        if task_type in ["complex_analysis", "detailed_reports", "reasoning"]:
            return OpenAIModel.GPT4_TURBO
        elif task_type in ["quick_responses", "simple_analysis"]:
            return OpenAIModel.GPT35_TURBO
        
        # Default to GPT-4 Turbo
        return OpenAIModel.GPT4_TURBO
    
    async def _call_openai_model(self, model: OpenAIModel, message: str, context: Dict[str, Any], task_type: str) -> str:
        """Call OpenAI API"""
        
        # Prepare system prompt based on task type
        system_prompt = self._get_system_prompt(task_type, context)
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        # Add context if available
        if context.get("conversation_history"):
            # Add recent conversation history
            for msg in context["conversation_history"][-5:]:  # Last 5 messages
                messages.insert(-1, {"role": msg["role"], "content": msg["content"]})
        
        # Prepare request payload
        payload = {
            "model": model.value,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        # Make API call
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error {response.status}: {error_text}")
                
                result = await response.json()
                
                if "choices" not in result or not result["choices"]:
                    raise Exception("No response from OpenAI API")
                
                return result["choices"][0]["message"]["content"].strip()
    
    def _get_system_prompt(self, task_type: str, context: Dict[str, Any]) -> str:
        """Get system prompt based on task type"""
        
        base_prompt = """You are an AI assistant specialized in software license management and cost optimization. 
        You help users analyze their software licenses, generate reports, provide recommendations, and answer questions about license utilization and costs.
        
        You have access to license data including:
        - License information (name, vendor, cost, utilization)
        - Usage metrics and trends
        - Cost analysis and forecasting
        - Recommendations for optimization
        
        Always provide helpful, accurate, and actionable insights about software license management."""
        
        if task_type == "response_generation":
            return base_prompt + """
            
            Generate natural, engaging responses that:
            - Are conversational and helpful
            - Include relevant data and insights
            - Provide actionable recommendations
            - Use appropriate emojis and formatting
            - Are specific to the user's request"""
        
        elif task_type == "analysis":
            return base_prompt + """
            
            Perform detailed analysis that:
            - Identifies key patterns and trends
            - Provides data-driven insights
            - Highlights cost optimization opportunities
            - Explains the reasoning behind recommendations
            - Uses clear, professional language"""
        
        elif task_type == "report_generation":
            return base_prompt + """
            
            Generate comprehensive reports that:
            - Are well-structured and professional
            - Include executive summaries
            - Provide detailed analysis and recommendations
            - Use appropriate formatting and sections
            - Are tailored to the target audience (AP, Procurement, Executive, etc.)"""
        
        elif task_type == "intent_recognition":
            return """You are an AI assistant that analyzes user messages to understand their intent for software license management tasks.

            Analyze the user's message and return a JSON response with the following structure:
            {
                "intent_category": "one of: dashboard, report, analysis, recommendation, forecast, comparison, greeting, help, unknown",
                "action": "one of: show, generate, analyze, recommend, forecast, compare, greet, help",
                "entities": {
                    "teams": ["list of mentioned teams like ap, procurement, executive"],
                    "time_period": "mentioned time period like last_quarter, next_month, etc.",
                    "licenses": ["list of mentioned license names"],
                    "metrics": ["list of mentioned metrics like cost, utilization, etc."]
                },
                "parameters": {
                    "urgency": "high/medium/low if mentioned",
                    "format": "report format if specified"
                },
                "confidence": 0.0-1.0
            }

            Intent categories:
            - dashboard: requests for overview, summary, current status
            - report: requests to generate reports for specific teams
            - analysis: requests to analyze trends, patterns, insights
            - recommendation: requests for suggestions, optimization advice
            - forecast: requests to predict future costs, usage, trends
            - comparison: requests to compare licenses, vendors, options
            - greeting: hello, hi, how are you, etc.
            - help: requests for assistance, guidance, capabilities
            - unknown: unclear or unrelated requests

            Extract relevant entities and parameters from the message. Be specific and accurate."""
        
        else:
            return base_prompt
    
    async def analyze_with_genai(self, data: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Perform analysis using Gen AI"""
        
        # Prepare analysis prompt
        analysis_prompt = f"""
        Please analyze the following license data for {analysis_type}:
        
        Data: {json.dumps(data, indent=2)}
        
        Provide:
        1. Key insights and patterns
        2. Cost optimization opportunities
        3. Recommendations for improvement
        4. Risk assessment if applicable
        """
        
        context = {
            "analysis_type": analysis_type,
            "data_summary": f"License data with {len(data)} items"
        }
        
        result = await self.process_with_genai(analysis_prompt, context, "analysis")
        
        return {
            "analysis": result,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat()
        }
    
    async def generate_report_with_genai(self, data: Dict[str, Any], report_type: str, team: str = "general") -> str:
        """Generate report using Gen AI"""
        
        # Prepare report prompt
        report_prompt = f"""
        Generate a {report_type} report for the {team} team based on the following license data:
        
        Data: {json.dumps(data, indent=2)}
        
        The report should include:
        1. Executive summary
        2. Key metrics and insights
        3. Cost analysis
        4. Recommendations
        5. Next steps
        
        Format it professionally for the {team} team.
        """
        
        context = {
            "report_type": report_type,
            "team": team,
            "data_summary": f"License data with {len(data)} items"
        }
        
        result = await self.process_with_genai(report_prompt, context, "report_generation")
        
        return result
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of available models"""
        
        return {
            "openai_configured": bool(self.openai_api_key),
            "anthropic_configured": False,  # Always false since we only use OpenAI
            "available_models": [
                {
                    "model": model.value,
                    "capabilities": capabilities,
                    "available": True
                }
                for model, capabilities in self.model_capabilities.items()
            ]
        }
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        
        return [
            {
                "model": model.value,
                "capabilities": capabilities,
                "available": True
            }
            for model, capabilities in self.model_capabilities.items()
        ]
    
    def get_model_capabilities(self, model: OpenAIModel) -> Dict[str, Any]:
        """Get capabilities for a specific model"""
        
        return self.model_capabilities.get(model, {})
    
    def is_model_available(self, model: OpenAIModel) -> bool:
        """Check if a model is available"""
        
        return model in self.model_capabilities and bool(self.openai_api_key)