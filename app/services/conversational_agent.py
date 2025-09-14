from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import asyncio

from ..models.chat_models import (
    ChatMessage, ChatResponse, Intent, ConversationContext, 
    ChatRequest, ChatHistory, IntentCategory, IntentAction
)
from .nlp_processor import NLPProcessor
from .report_customizer import ReportCustomizer
from .genai_service import GenAIService
from ..utils.data_manager import DataManager


class ConversationalAgent:
    """Conversational AI agent with OpenAI integration"""
    
    def __init__(self):
        self.nlp_processor = NLPProcessor()
        self.report_customizer = ReportCustomizer()
        self.genai_service = GenAIService()
        self.data_manager = DataManager()
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        self.chat_histories: Dict[str, ChatHistory] = {}
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a user message with enhanced Gen AI capabilities"""
        
        # Get or create conversation context
        session_id = request.session_id or str(uuid.uuid4())
        context = self._get_or_create_context(request.user_id, session_id)
        
        # Parse the user's intent using enhanced NLP
        intent = await self.nlp_processor.parse_intent(request.message, {
            "conversation_history": self._get_recent_conversation_history(session_id),
            "user_preferences": context.user_preferences
        })
        
        # Create chat message
        chat_message = ChatMessage(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            message=request.message,
            timestamp=datetime.now(),
            intent=intent.category,
            action=intent.action,
            entities=intent.entities,
            parameters=intent.parameters,
            context=request.context
        )
        
        # Update conversation context
        self._update_context(context, intent)
        
        # Generate response using Gen AI
        response = await self._generate_enhanced_response(intent, context, request)
        
        # Store in chat history
        self._store_chat_interaction(session_id, request.user_id, chat_message, response)
        
        return response
    
    def _get_or_create_context(self, user_id: str, session_id: str) -> ConversationContext:
        """Get existing context or create new one"""
        context_key = f"{user_id}_{session_id}"
        
        if context_key not in self.conversation_contexts:
            self.conversation_contexts[context_key] = ConversationContext(
                user_id=user_id,
                session_id=session_id
            )
        
        return self.conversation_contexts[context_key]
    
    def _get_recent_conversation_history(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation history for context"""
        
        if session_id not in self.chat_histories:
            return []
        
        history = self.chat_histories[session_id]
        recent_messages = []
        
        # Get last few messages and responses
        for i in range(max(0, len(history.messages) - limit), len(history.messages)):
            if i < len(history.messages):
                recent_messages.append({
                    "role": "user",
                    "content": history.messages[i].message,
                    "timestamp": history.messages[i].timestamp.isoformat()
                })
            
            if i < len(history.responses):
                recent_messages.append({
                    "role": "ai",
                    "content": history.responses[i].message,
                    "timestamp": history.responses[i].timestamp.isoformat() if hasattr(history.responses[i], 'timestamp') else datetime.now().isoformat()
                })
        
        return recent_messages
    
    def _update_context(self, context: ConversationContext, intent: Intent):
        """Update conversation context with new intent"""
        context.previous_intents.append(intent.category)
        context.current_topic = intent.category.value
        
        # Update preferences based on entities
        if intent.entities.get("teams"):
            context.user_preferences["preferred_team"] = intent.entities["teams"][0]
        
        if intent.entities.get("time_period"):
            context.user_preferences["preferred_time_period"] = intent.entities["time_period"]
        
        if intent.category == IntentCategory.REPORT:
            context.last_report_type = intent.entities.get("teams", ["general"])[0]
        
        if intent.category == IntentCategory.ANALYSIS:
            context.last_analysis_focus = intent.entities.get("metrics", ["general"])[0]
        
        context.updated_at = datetime.now()
    
    async def _generate_enhanced_response(self, intent: Intent, context: ConversationContext, 
                                        request: ChatRequest) -> ChatResponse:
        """Generate enhanced response using Gen AI"""
        
        # Handle greetings
        if intent.category == IntentCategory.GREETING:
            return await self._generate_greeting_response(context)
        
        # Handle help requests
        if intent.category == IntentCategory.HELP:
            return await self._generate_help_response()
        
        # Handle unknown intents
        if intent.category == IntentCategory.UNKNOWN:
            return await self._generate_unknown_response()
        
        # Generate data-driven response with Gen AI enhancement
        try:
            # Get custom report data
            report_data = self.report_customizer.generate_custom_report(intent, context.user_preferences)
            
            # Generate enhanced response using Gen AI
            enhanced_message = await self._generate_enhanced_message(intent, report_data, context)
            
            # Generate suggestions using Gen AI
            suggestions = await self._generate_enhanced_suggestions(intent, report_data, context)
            
            # Generate follow-up questions using Gen AI
            follow_up_questions = await self.nlp_processor.generate_follow_up_questions(intent, {
                "conversation_history": self._get_recent_conversation_history(context.session_id),
                "user_preferences": context.user_preferences
            })
            
            # Determine response type
            response_type = self._determine_response_type(intent, report_data)
            
            return ChatResponse(
                message=enhanced_message,
                data=report_data,
                report=report_data if intent.category == IntentCategory.REPORT else None,
                visualizations=report_data.get("visualizations", []) if response_type == "mixed" else None,
                suggestions=suggestions,
                follow_up_questions=follow_up_questions,
                confidence=intent.confidence,
                response_type=response_type
            )
            
        except Exception as e:
            # Fallback to simple error response
            return ChatResponse(
                message=f"I encountered an error while processing your request: {str(e)}. Please try rephrasing your question.",
                confidence=0.0,
                response_type="text"
            )
    
    async def _generate_greeting_response(self, context: ConversationContext) -> ChatResponse:
        """Generate enhanced greeting response using Gen AI"""
        
        try:
            # Use Gen AI to generate personalized greeting
            genai_context = {
                "user_preferences": context.user_preferences,
                "previous_intents": [intent.value for intent in context.previous_intents[-3:]]  # Last 3 intents
            }
            
            genai_result = await self.genai_service.process_with_genai(
                message="Generate a personalized greeting for a software license management assistant",
                context=genai_context,
                task_type="response_generation"
            )
            
            if genai_result["success"]:
                message = genai_result["response"]
            else:
                message = "Hello! I'm your AI assistant for software license management. How can I help you today?"
        except Exception as e:
            print(f"Gen AI greeting generation failed: {e}")
            message = "Hello! I'm your AI assistant for software license management. How can I help you today?"
        
        suggestions = [
            "Show me the dashboard",
            "Generate an AP team report",
            "What are the cost optimization opportunities?",
            "Analyze license utilization trends"
        ]
        
        return ChatResponse(
            message=message,
            suggestions=suggestions,
            confidence=1.0,
            response_type="text"
        )
    
    async def _generate_help_response(self) -> ChatResponse:
        """Generate enhanced help response using Gen AI"""
        
        try:
            genai_result = await self.genai_service.process_with_genai(
                message="Generate a comprehensive help message for a software license management AI assistant",
                context={"capabilities": ["dashboard", "reports", "analysis", "recommendations", "forecasting", "comparisons"]},
                task_type="response_generation"
            )
            
            if genai_result["success"]:
                message = genai_result["response"]
            else:
                message = self._get_fallback_help_message()
        except Exception as e:
            print(f"Gen AI help generation failed: {e}")
            message = self._get_fallback_help_message()
        
        suggestions = [
            "Show me the dashboard",
            "Generate an AP team report",
            "What are the cost optimization opportunities?",
            "Analyze license utilization trends"
        ]
        
        return ChatResponse(
            message=message,
            suggestions=suggestions,
            confidence=1.0,
            response_type="text"
        )
    
    def _get_fallback_help_message(self) -> str:
        """Fallback help message"""
        return """I can help you with several tasks:

📊 **Dashboard & Overview**: Show current license status, costs, and utilization
📋 **Reports**: Generate custom reports for AP, Procurement, or Executive teams
🔍 **Analysis**: Analyze usage patterns, trends, and performance metrics
💡 **Recommendations**: Get AI-powered suggestions for cost optimization
🔮 **Forecasting**: Predict future usage and costs
⚖️ **Comparisons**: Compare different licenses or vendors

Try asking me things like:
• "Show me the dashboard"
• "Generate a quarterly report for our AP team"
• "Which licenses should we cancel to save money?"
• "Compare Zoom and Slack usage"
• "What are the cost trends for the last quarter?"
"""
    
    async def _generate_unknown_response(self) -> ChatResponse:
        """Generate enhanced unknown response using Gen AI"""
        
        try:
            genai_result = await self.genai_service.process_with_genai(
                message="Generate a helpful response for when you don't understand a user's request about software license management",
                context={"capabilities": ["dashboard", "reports", "analysis", "recommendations", "forecasting", "comparisons"]},
                task_type="response_generation"
            )
            
            if genai_result["success"]:
                message = genai_result["response"]
            else:
                message = self._get_fallback_unknown_message()
        except Exception as e:
            print(f"Gen AI unknown response generation failed: {e}")
            message = self._get_fallback_unknown_message()
        
        suggestions = [
            "Show me the dashboard",
            "Generate an AP team report",
            "What are the cost optimization opportunities?",
            "Help me get started"
        ]
        
        return ChatResponse(
            message=message,
            suggestions=suggestions,
            confidence=0.3,
            response_type="text"
        )
    
    def _get_fallback_unknown_message(self) -> str:
        """Fallback unknown message"""
        return """I'm not sure I understand your request. I can help you with:

• Dashboard overviews and summaries
• Custom reports for different teams
• License analysis and trends
• Cost optimization recommendations
• Usage forecasting
• License comparisons

Could you try rephrasing your question or ask me to help you get started?"""
    
    async def _generate_enhanced_message(self, intent: Intent, report_data: Dict[str, Any], 
                                       context: ConversationContext) -> str:
        """Generate enhanced response message using Gen AI"""
        
        # Prepare context for Gen AI
        genai_context = {
            "intent": intent.model_dump(),
            "report_data": report_data,
            "user_preferences": context.user_preferences,
            "conversation_history": self._get_recent_conversation_history(context.session_id)
        }
        
        # Create prompt based on intent category
        if intent.category == IntentCategory.DASHBOARD:
            prompt = f"Generate a natural, engaging response for a dashboard overview with this data: {report_data.get('summary', {})}"
        elif intent.category == IntentCategory.REPORT:
            prompt = f"Generate a professional report summary for {intent.entities.get('teams', ['general'])[0]} team with this data: {report_data}"
        elif intent.category == IntentCategory.ANALYSIS:
            prompt = f"Generate an analytical response about license analysis with these insights: {report_data.get('insights', [])}"
        elif intent.category == IntentCategory.RECOMMENDATION:
            prompt = f"Generate a recommendation response with these suggestions: {report_data.get('recommendations', [])}"
        elif intent.category == IntentCategory.FORECAST:
            prompt = f"Generate a forecast response with this data: {report_data.get('license_forecasts', [])}"
        elif intent.category == IntentCategory.COMPARISON:
            prompt = f"Generate a comparison response with this data: {report_data.get('comparison_data', [])}"
        else:
            prompt = f"Generate a helpful response based on this data: {report_data}"
        
        try:
            genai_result = await self.genai_service.process_with_genai(
                message=prompt,
                context=genai_context,
                task_type="response_generation"
            )
            
            if genai_result["success"]:
                return genai_result["response"]
        except Exception as e:
            print(f"Gen AI message generation failed: {e}")
        
        # Fallback to rule-based message generation
        return self._generate_fallback_message(intent, report_data)
    
    def _generate_fallback_message(self, intent: Intent, report_data: Dict[str, Any]) -> str:
        """Generate fallback message using rule-based approach"""
        
        if intent.category == IntentCategory.DASHBOARD:
            return self._generate_dashboard_message_fallback(report_data)
        elif intent.category == IntentCategory.REPORT:
            return self._generate_report_message_fallback(report_data, intent)
        elif intent.category == IntentCategory.ANALYSIS:
            return self._generate_analysis_message_fallback(report_data, intent)
        elif intent.category == IntentCategory.RECOMMENDATION:
            return self._generate_recommendation_message_fallback(report_data, intent)
        elif intent.category == IntentCategory.FORECAST:
            return self._generate_forecast_message_fallback(report_data, intent)
        elif intent.category == IntentCategory.COMPARISON:
            return self._generate_comparison_message_fallback(report_data, intent)
        else:
            return "Here's the information you requested:"
    
    def _generate_dashboard_message_fallback(self, report_data: Dict[str, Any]) -> str:
        """Fallback dashboard message generation"""
        summary = report_data.get("summary", {})
        total_licenses = summary.get("total_licenses", 0)
        total_cost = summary.get("total_cost", 0)
        avg_utilization = summary.get("average_utilization", 0)
        
        message = f"""Here's your current license dashboard:

📊 **Overview:**
• Total Licenses: {total_licenses}
• Total Annual Cost: ${total_cost:,.0f}
• Average Utilization: {avg_utilization:.1f}%

"""
        
        insights = report_data.get("insights", [])
        if insights:
            message += "🔍 **Key Insights:**\n"
            for insight in insights[:3]:
                message += f"• {insight}\n"
        
        return message
    
    def _generate_report_message_fallback(self, report_data: Dict[str, Any], intent: Intent) -> str:
        """Fallback report message generation"""
        report_type = report_data.get("report_type", "general")
        
        if report_type == "ap_team":
            return self._generate_ap_report_message_fallback(report_data)
        elif report_type == "procurement":
            return self._generate_procurement_report_message_fallback(report_data)
        elif report_type == "executive":
            return self._generate_executive_report_message_fallback(report_data)
        else:
            return self._generate_general_report_message_fallback(report_data)
    
    def _generate_ap_report_message_fallback(self, report_data: Dict[str, Any]) -> str:
        """Fallback AP report message"""
        budget_impact = report_data.get("budget_impact", {})
        upcoming_renewals = report_data.get("upcoming_renewals", [])
        
        message = f"""📋 **AP Team Report Generated**

💰 **Budget Impact:**
• Annual Cost: ${budget_impact.get('total_annual', 0):,.0f}
• Monthly Cost: ${budget_impact.get('monthly', 0):,.0f}
• Quarterly Cost: ${budget_impact.get('quarterly', 0):,.0f}

"""
        
        if upcoming_renewals:
            message += f"⏰ **Upcoming Renewals ({len(upcoming_renewals)}):**\n"
            for renewal in upcoming_renewals[:3]:
                message += f"• {renewal['license']}: ${renewal['cost']:,.0f} (expires in {renewal['days_to_expiry']} days)\n"
        else:
            message += "✅ No urgent renewals in the next 90 days\n"
        
        return message
    
    def _generate_procurement_report_message_fallback(self, report_data: Dict[str, Any]) -> str:
        """Fallback procurement report message"""
        vendor_analysis = report_data.get("vendor_analysis", {})
        negotiation_opportunities = report_data.get("negotiation_opportunities", [])
        
        message = f"""📋 **Procurement Team Report Generated**

🏢 **Vendor Analysis ({len(vendor_analysis)} vendors):**\n"""
        
        sorted_vendors = sorted(vendor_analysis.items(), key=lambda x: x[1]["total_cost"], reverse=True)
        for vendor, data in sorted_vendors[:3]:
            message += f"• {vendor}: {data['count']} licenses, ${data['total_cost']:,.0f}\n"
        
        if negotiation_opportunities:
            message += f"\n💡 **Negotiation Opportunities ({len(negotiation_opportunities)}):**\n"
            for opp in negotiation_opportunities[:3]:
                message += f"• {opp['license']}: {opp['opportunity']}\n"
        
        return message
    
    def _generate_executive_report_message_fallback(self, report_data: Dict[str, Any]) -> str:
        """Fallback executive report message"""
        executive_summary = report_data.get("executive_summary", {})
        
        message = f"""📋 **Executive Summary Report**

🎯 **Key Metrics:**
• Total Software Spend: ${executive_summary.get('total_software_spend', 0):,.0f}
• License Count: {executive_summary.get('license_count', 0)}
• Average Utilization: {executive_summary.get('average_utilization', 0):.1f}%
• Optimization Potential: {executive_summary.get('optimization_potential', 'medium').title()}

"""
        
        strategic_recommendations = report_data.get("strategic_recommendations", [])
        if strategic_recommendations:
            message += "🎯 **Strategic Recommendations:**\n"
            for rec in strategic_recommendations[:3]:
                message += f"• {rec}\n"
        
        return message
    
    def _generate_general_report_message_fallback(self, report_data: Dict[str, Any]) -> str:
        """Fallback general report message"""
        summary = report_data.get("summary", {})
        
        message = f"""📋 **Report Generated**

📊 **Summary:**
• Total Licenses: {summary.get('total_licenses', 0)}
• Total Cost: ${summary.get('total_cost', 0):,.0f}
• Average Utilization: {summary.get('average_utilization', 0):.1f}%

"""
        
        insights = report_data.get("insights", [])
        if insights:
            message += "🔍 **Key Insights:**\n"
            for insight in insights[:3]:
                message += f"• {insight}\n"
        
        return message
    
    def _generate_analysis_message_fallback(self, report_data: Dict[str, Any], intent: Intent) -> str:
        """Fallback analysis message"""
        focus = intent.entities.get("metrics", ["general"])
        detailed_analysis = report_data.get("detailed_analysis", [])
        
        message = f"""🔍 **Analysis Complete**

Focus: {', '.join(focus) if isinstance(focus, list) else focus}
Time Period: {report_data.get('time_period', 'all_time')}

"""
        
        if detailed_analysis:
            message += "📊 **Analysis Results:**\n"
            for analysis in detailed_analysis[:3]:
                license_name = analysis["license"]
                utilization_stats = analysis["analysis"].get("utilization_stats", {})
                avg_utilization = utilization_stats.get("mean", 0)
                message += f"• {license_name}: {avg_utilization:.1f}% average utilization\n"
        
        summary_insights = report_data.get("summary_insights", [])
        if summary_insights:
            message += "\n💡 **Key Insights:**\n"
            for insight in summary_insights[:3]:
                message += f"• {insight}\n"
        
        return message
    
    def _generate_recommendation_message_fallback(self, report_data: Dict[str, Any], intent: Intent) -> str:
        """Fallback recommendation message"""
        total_savings = report_data.get("total_potential_savings", 0)
        recommendations = report_data.get("recommendations", [])
        priority_actions = report_data.get("priority_actions", [])
        
        message = f"""💡 **AI Recommendations Generated**

💰 **Total Potential Savings: ${total_savings:,.0f}**

"""
        
        if priority_actions:
            message += "🚨 **High Priority Actions:**\n"
            for rec in priority_actions[:3]:
                message += f"• {rec['license']}: {rec['recommendation']} (saves ${rec['estimated_savings']:,.0f})\n"
        
        if recommendations:
            message += f"\n📋 **All Recommendations ({len(recommendations)}):**\n"
            for rec in recommendations[:5]:
                priority_emoji = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
                message += f"{priority_emoji} {rec['license']}: {rec['recommendation']}\n"
        
        return message
    
    def _generate_forecast_message_fallback(self, report_data: Dict[str, Any], intent: Intent) -> str:
        """Fallback forecast message"""
        forecast_horizon = report_data.get("forecast_horizon", "90_days")
        license_forecasts = report_data.get("license_forecasts", [])
        overall_trends = report_data.get("overall_trends", {})
        
        message = f"""🔮 **Forecast Analysis Complete**

📅 **Forecast Horizon:** {forecast_horizon.replace('_', ' ').title()}
📈 **Overall Trend:** {overall_trends.get('dominant_trend', 'stable').title()}

"""
        
        if license_forecasts:
            message += "📊 **License Forecasts:**\n"
            for forecast in license_forecasts[:3]:
                license_name = forecast["license"]
                summary = forecast["summary"]
                avg_usage = summary.get("average_predicted_usage", 0)
                avg_cost = summary.get("average_predicted_cost", 0)
                confidence = summary.get("average_confidence", 0)
                message += f"• {license_name}: {avg_usage:.0f} usage, ${avg_cost:.0f} cost (confidence: {confidence:.1%})\n"
        
        confidence_scores = report_data.get("confidence_scores", {})
        if confidence_scores:
            overall_confidence = confidence_scores.get("overall_confidence", 0)
            message += f"\n🎯 **Overall Forecast Confidence:** {overall_confidence:.1%}\n"
        
        return message
    
    def _generate_comparison_message_fallback(self, report_data: Dict[str, Any], intent: Intent) -> str:
        """Fallback comparison message"""
        licenses_compared = report_data.get("licenses_compared", 0)
        comparison_data = report_data.get("comparison_data", [])
        rankings = report_data.get("rankings", {})
        
        message = f"""⚖️ **Comparison Analysis Complete**

📊 **Licenses Compared:** {licenses_compared}

"""
        
        if comparison_data:
            message += "📋 **Comparison Results:**\n"
            for data in comparison_data:
                message += f"• {data['license']}: ${data['cost']:,.0f} cost, {data['utilization']:.1f}% utilization\n"
        
        if rankings:
            by_efficiency = rankings.get("by_efficiency", [])
            if by_efficiency:
                most_efficient = by_efficiency[0]
                message += f"\n🏆 **Most Efficient:** {most_efficient['license']} (efficiency score: {most_efficient['efficiency_score']:.2f})\n"
        
        insights = report_data.get("insights", [])
        if insights:
            message += "\n💡 **Comparison Insights:**\n"
            for insight in insights[:3]:
                message += f"• {insight}\n"
        
        return message
    
    async def _generate_enhanced_suggestions(self, intent: Intent, report_data: Dict[str, Any], 
                                           context: ConversationContext) -> List[str]:
        """Generate enhanced suggestions using Gen AI"""
        
        try:
            genai_context = {
                "intent": intent.model_dump(),
                "report_data": report_data,
                "user_preferences": context.user_preferences,
                "conversation_history": self._get_recent_conversation_history(context.session_id)
            }
            
            genai_result = await self.genai_service.process_with_genai(
                message=f"Generate 3-4 relevant follow-up suggestions for a {intent.category.value} request",
                context=genai_context,
                task_type="response_generation"
            )
            
            if genai_result["success"]:
                # Extract suggestions from Gen AI response
                suggestions = self._extract_suggestions_from_genai_response(genai_result["response"])
                if suggestions:
                    return suggestions
        except Exception as e:
            print(f"Gen AI suggestion generation failed: {e}")
        
        # Fallback to rule-based suggestions
        return self._generate_fallback_suggestions(intent, report_data)
    
    def _extract_suggestions_from_genai_response(self, response: str) -> List[str]:
        """Extract suggestions from Gen AI response"""
        
        suggestions = []
        
        # Look for suggestion patterns
        suggestion_patterns = [
            r"• (.+?)(?:\n|$)",
            r"- (.+?)(?:\n|$)",
            r"\d+\. (.+?)(?:\n|$)"
        ]
        
        for pattern in suggestion_patterns:
            matches = re.findall(pattern, response, re.MULTILINE)
            for match in matches:
                suggestion = match.strip()
                if len(suggestion) > 10 and len(suggestion) < 100:  # Reasonable length
                    suggestions.append(suggestion)
        
        return suggestions[:4]  # Return max 4 suggestions
    
    def _generate_fallback_suggestions(self, intent: Intent, report_data: Dict[str, Any]) -> List[str]:
        """Generate fallback suggestions using rule-based approach"""
        
        if intent.category == IntentCategory.DASHBOARD:
            return [
                "Generate an AP team report",
                "Show cost optimization opportunities",
                "Analyze utilization trends"
            ]
        elif intent.category == IntentCategory.REPORT:
            return [
                "Generate a different team report",
                "Show detailed analysis",
                "Get cost optimization recommendations"
            ]
        elif intent.category == IntentCategory.ANALYSIS:
            return [
                "Generate a report based on this analysis",
                "Get recommendations for underperforming licenses",
                "Compare with other time periods"
            ]
        elif intent.category == IntentCategory.RECOMMENDATION:
            return [
                "Generate a detailed implementation plan",
                "Show forecast for recommended changes",
                "Create a cost savings report"
            ]
        elif intent.category == IntentCategory.FORECAST:
            return [
                "Get recommendations based on forecasts",
                "Compare with historical trends",
                "Generate budget planning report"
            ]
        elif intent.category == IntentCategory.COMPARISON:
            return [
                "Get recommendations for the best option",
                "Show detailed analysis of top performers",
                "Generate cost optimization plan"
            ]
        else:
            return [
                "Show me the dashboard",
                "Generate an AP team report",
                "What are the cost optimization opportunities?"
            ]
    
    def _determine_response_type(self, intent: Intent, report_data: Dict[str, Any]) -> str:
        """Determine the type of response to return"""
        
        if intent.category == IntentCategory.REPORT:
            return "report"
        elif report_data.get("visualizations"):
            return "mixed"
        else:
            return "text"
    
    def _store_chat_interaction(self, session_id: str, user_id: str, 
                              message: ChatMessage, response: ChatResponse):
        """Store chat interaction in history"""
        
        if session_id not in self.chat_histories:
            self.chat_histories[session_id] = ChatHistory(
                session_id=session_id,
                user_id=user_id
            )
        
        history = self.chat_histories[session_id]
        history.messages.append(message)
        history.responses.append(response)
        history.updated_at = datetime.now()
    
    def get_chat_history(self, session_id: str) -> Optional[ChatHistory]:
        """Get chat history for a session"""
        return self.chat_histories.get(session_id)
    
    def get_conversation_context(self, user_id: str, session_id: str) -> Optional[ConversationContext]:
        """Get conversation context for a user session"""
        context_key = f"{user_id}_{session_id}"
        return self.conversation_contexts.get(context_key)
    
    def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get information about agent capabilities"""
        
        return {
            "genai_available": bool(self.genai_service.openai_api_key),
            "genai_models": self.genai_service.get_available_models(),
            "nlp_capabilities": self.nlp_processor.get_processing_capabilities(),
            "supported_intents": [category.value for category in IntentCategory],
            "supported_actions": [action.value for action in IntentAction],
            "conversation_contexts": len(self.conversation_contexts),
            "chat_histories": len(self.chat_histories)
        }

