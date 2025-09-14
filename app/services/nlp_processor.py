import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timedelta
import json
import re

from ..models.chat_models import Intent, IntentCategory, IntentAction
from .genai_service import GenAIService


class NLPProcessor:
    """NLP processor using OpenAI for intent recognition and understanding"""
    
    def __init__(self):
        self.genai_service = GenAIService()
        self.fallback_patterns = self._initialize_fallback_patterns()
        self.license_names = self._get_license_names()
        
    def _initialize_fallback_patterns(self) -> Dict[str, List[str]]:
        """Initialize fallback regex patterns for when Gen AI is not available"""
        return {
            "dashboard": [
                r"show.*dashboard", r"dashboard", r"overview", r"summary", 
                r"main.*page", r"home", r"current.*status"
            ],
            "report": [
                r"generate.*report", r"create.*report", r"report", r"ap.*report",
                r"procurement.*report", r"financial.*report", r"quarterly.*report",
                r"monthly.*report", r"annual.*report", r"custom.*report"
            ],
            "analysis": [
                r"analyze", r"analysis", r"trends", r"patterns", r"insights",
                r"what.*happening", r"how.*performing", r"usage.*analysis"
            ],
            "recommendation": [
                r"recommend", r"suggest", r"what.*should", r"optimize", r"save.*money",
                r"reduce.*cost", r"cut.*cost", r"which.*cancel", r"which.*renew"
            ],
            "forecast": [
                r"forecast", r"predict", r"future", r"projection", r"next.*month",
                r"next.*quarter", r"next.*year", r"what.*will.*happen"
            ],
            "comparison": [
                r"compare", r"vs", r"versus", r"difference", r"better", r"worse",
                r"which.*better", r"which.*cheaper", r"which.*more.*efficient"
            ],
            "greeting": [
                r"hello", r"hi", r"hey", r"good.*morning", r"good.*afternoon",
                r"good.*evening", r"how.*are.*you", r"what.*can.*you.*do"
            ],
            "help": [
                r"help", r"what.*can.*you", r"how.*to", r"guide", r"tutorial",
                r"commands", r"features", r"capabilities"
            ]
        }
    
    def _get_license_names(self) -> List[str]:
        """Get list of known license names"""
        return [
            "workato", "workato integration platform", "slack", "slack business+",
            "aws", "aws enterprise support", "salesforce", "salesforce enterprise",
            "zoom", "zoom pro", "jira", "jira software", "atlassian"
        ]
    
    async def parse_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Intent:
        """Parse user message using Gen AI with fallback to rule-based approach"""
        
        # Try Gen AI first
        try:
            genai_result = await self._parse_with_genai(message, context)
            if genai_result["success"]:
                return self._convert_genai_result_to_intent(genai_result["response"], message)
        except Exception as e:
            print(f"Gen AI intent parsing failed: {e}")
        
        # Fallback to rule-based approach
        return self._parse_with_fallback(message)
    
    async def _parse_with_genai(self, message: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse intent using Gen AI"""
        
        # Prepare context for Gen AI
        genai_context = {
            "conversation_history": context.get("conversation_history", []) if context else [],
            "user_preferences": context.get("user_preferences", {}) if context else {},
            "available_licenses": self.license_names
        }
        
        return await self.genai_service.process_with_genai(
            message=message,
            context=genai_context,
            task_type="intent_recognition"
        )
    
    def _convert_genai_result_to_intent(self, genai_response: str, original_message: str) -> Intent:
        """Convert Gen AI response to Intent object"""
        
        try:
            # Try to parse as JSON
            parsed = json.loads(genai_response)
            
            return Intent(
                category=IntentCategory(parsed.get("intent_category", "unknown")),
                action=IntentAction(parsed.get("action", "show")),
                entities=parsed.get("entities", {}),
                parameters=parsed.get("parameters", {}),
                confidence=float(parsed.get("confidence", 0.8)),
                original_message=original_message
            )
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse Gen AI response: {e}")
            # Fallback to rule-based parsing
            return self._parse_with_fallback(original_message)
    
    def _parse_with_fallback(self, message: str) -> Intent:
        """Fallback rule-based intent parsing"""
        
        message_lower = message.lower().strip()
        
        # Find best matching intent category
        intent_category, category_confidence = self._classify_intent_category_fallback(message_lower)
        
        # Extract action
        action = self._extract_action_fallback(message_lower)
        
        # Extract entities
        entities = self._extract_entities_fallback(message_lower)
        
        # Extract parameters
        parameters = self._extract_parameters_fallback(message_lower, entities)
        
        # Calculate overall confidence
        confidence = self._calculate_confidence_fallback(category_confidence, entities, parameters)
        
        return Intent(
            category=intent_category,
            action=action,
            entities=entities,
            parameters=parameters,
            confidence=confidence,
            original_message=message
        )
    
    def _classify_intent_category_fallback(self, message: str) -> Tuple[IntentCategory, float]:
        """Fallback intent category classification"""
        
        best_category = IntentCategory.UNKNOWN
        best_score = 0.0
        
        for category, patterns in self.fallback_patterns.items():
            score = 0.0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    matches += 1
                    score += len(pattern.split()) * 0.1
            
            if matches > 0:
                score = min(score / len(patterns), 1.0)
                
                if score > best_score:
                    best_score = score
                    best_category = IntentCategory(category)
        
        return best_category, best_score
    
    def _extract_action_fallback(self, message: str) -> IntentAction:
        """Fallback action extraction"""
        
        action_patterns = {
            IntentAction.SHOW: [r"show", r"display", r"view", r"see"],
            IntentAction.GENERATE: [r"generate", r"create", r"make", r"build"],
            IntentAction.COMPARE: [r"compare", r"vs", r"versus", r"against"],
            IntentAction.ANALYZE: [r"analyze", r"analysis", r"examine", r"study"],
            IntentAction.RECOMMEND: [r"recommend", r"suggest", r"advise", r"propose"],
            IntentAction.FORECAST: [r"forecast", r"predict", r"project", r"estimate"],
            IntentAction.OPTIMIZE: [r"optimize", r"improve", r"enhance", r"maximize"],
            IntentAction.EXPLAIN: [r"explain", r"describe", r"tell.*about", r"what.*is"],
            IntentAction.GREET: [r"hello", r"hi", r"hey", r"good.*morning"],
            IntentAction.HELP: [r"help", r"assist", r"guide", r"support"]
        }
        
        for action, patterns in action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return action
        
        return IntentAction.SHOW
    
    def _extract_entities_fallback(self, message: str) -> Dict[str, Any]:
        """Fallback entity extraction"""
        
        entities = {}
        
        # Extract time periods
        time_period = self._extract_time_period_fallback(message)
        if time_period:
            entities["time_period"] = time_period
        
        # Extract license names
        licenses = self._extract_license_names_fallback(message)
        if licenses:
            entities["licenses"] = licenses
        
        # Extract metrics
        metrics = self._extract_metrics_fallback(message)
        if metrics:
            entities["metrics"] = metrics
        
        # Extract team references
        teams = self._extract_teams_fallback(message)
        if teams:
            entities["teams"] = teams
        
        return entities
    
    def _extract_time_period_fallback(self, message: str) -> Optional[Dict[str, Any]]:
        """Fallback time period extraction"""
        
        # Days
        days_match = re.search(r"last.*(\d+).*days?", message)
        if days_match:
            days = int(days_match.group(1))
            return {
                "type": "days",
                "value": days,
                "start_date": (date.today() - timedelta(days=days)).isoformat(),
                "end_date": date.today().isoformat()
            }
        
        # Weeks
        if re.search(r"last.*week", message):
            return {
                "type": "week",
                "value": 1,
                "start_date": (date.today() - timedelta(days=7)).isoformat(),
                "end_date": date.today().isoformat()
            }
        
        # Months
        if re.search(r"last.*month", message):
            return {
                "type": "month",
                "value": 1,
                "start_date": (date.today() - timedelta(days=30)).isoformat(),
                "end_date": date.today().isoformat()
            }
        
        # Quarters
        quarter_match = re.search(r"q([1-4])", message)
        if quarter_match:
            quarter = int(quarter_match.group(1))
            return {
                "type": "quarter",
                "value": quarter,
                "year": date.today().year
            }
        
        return None
    
    def _extract_license_names_fallback(self, message: str) -> List[str]:
        """Fallback license name extraction"""
        
        found_licenses = []
        
        for license_name in self.license_names:
            if license_name.lower() in message.lower():
                found_licenses.append(license_name)
        
        return found_licenses
    
    def _extract_metrics_fallback(self, message: str) -> List[str]:
        """Fallback metric extraction"""
        
        metrics = []
        
        for metric in ["cost", "usage", "utilization", "spending", "budget", "efficiency"]:
            if metric in message.lower():
                metrics.append(metric)
        
        return metrics
    
    def _extract_teams_fallback(self, message: str) -> List[str]:
        """Fallback team extraction"""
        
        teams = []
        
        team_patterns = {
            "ap": [r"ap.*team", r"accounts.*payable"],
            "procurement": [r"procurement", r"purchasing"],
            "finance": [r"finance", r"financial"],
            "executive": [r"executive", r"cfo", r"cto", r"management"]
        }
        
        for team, patterns in team_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    teams.append(team)
                    break
        
        return teams
    
    def _extract_parameters_fallback(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback parameter extraction"""
        
        parameters = {}
        
        # Extract detail level
        if re.search(r"detailed|comprehensive|full", message):
            parameters["detail_level"] = "detailed"
        elif re.search(r"summary|brief|overview", message):
            parameters["detail_level"] = "summary"
        else:
            parameters["detail_level"] = "standard"
        
        # Extract format preferences
        if re.search(r"pdf|document", message):
            parameters["format"] = "pdf"
        elif re.search(r"excel|spreadsheet", message):
            parameters["format"] = "excel"
        else:
            parameters["format"] = "json"
        
        # Extract visualization preferences
        parameters["include_visualizations"] = not re.search(r"no.*chart|no.*graph|no.*visual", message)
        
        # Extract forecast preferences
        parameters["include_forecasts"] = re.search(r"forecast|predict|future", message) is not None
        
        # Extract recommendation preferences
        parameters["include_recommendations"] = re.search(r"recommend|suggest|advice", message) is not None
        
        return parameters
    
    def _calculate_confidence_fallback(self, category_confidence: float, entities: Dict[str, Any], 
                                     parameters: Dict[str, Any]) -> float:
        """Fallback confidence calculation"""
        
        confidence = category_confidence
        
        # Boost confidence if we found relevant entities
        if entities:
            confidence += 0.1
        
        # Boost confidence if we found specific parameters
        if parameters.get("detail_level") != "standard":
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    async def generate_follow_up_questions(self, intent: Intent, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generate follow-up questions using Gen AI with fallback"""
        
        # Try Gen AI first
        try:
            genai_context = {
                "intent": intent.model_dump(),
                "conversation_history": context.get("conversation_history", []) if context else []
            }
            
            genai_result = await self.genai_service.process_with_genai(
                message=f"Generate relevant follow-up questions for this intent: {intent.category.value}",
                context=genai_context,
                task_type="response_generation"
            )
            
            if genai_result["success"]:
                # Parse Gen AI response for questions
                questions = self._extract_questions_from_genai_response(genai_result["response"])
                if questions:
                    return questions
        except Exception as e:
            print(f"Gen AI follow-up generation failed: {e}")
        
        # Fallback to rule-based approach
        return self._generate_follow_up_questions_fallback(intent)
    
    def _extract_questions_from_genai_response(self, response: str) -> List[str]:
        """Extract questions from Gen AI response"""
        
        questions = []
        
        # Look for question patterns
        question_patterns = [
            r"Would you like to (.+?)\?",
            r"Are you interested in (.+?)\?",
            r"Would you prefer (.+?)\?",
            r"Should I (.+?)\?",
            r"Do you want (.+?)\?"
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                questions.append(match.strip())
        
        return questions[:3]  # Return max 3 questions
    
    def _generate_follow_up_questions_fallback(self, intent: Intent) -> List[str]:
        """Fallback follow-up question generation"""
        
        questions = []
        
        if intent.category == IntentCategory.REPORT:
            if not intent.entities.get("teams"):
                questions.append("Which team is this report for? (AP, Procurement, Executive)")
            if not intent.entities.get("time_period"):
                questions.append("What time period would you like to analyze?")
        
        elif intent.category == IntentCategory.ANALYSIS:
            if not intent.entities.get("licenses"):
                questions.append("Which specific licenses would you like me to analyze?")
            if not intent.entities.get("metrics"):
                questions.append("What metrics are you most interested in? (cost, usage, efficiency)")
        
        elif intent.category == IntentCategory.RECOMMENDATION:
            questions.append("What's your target cost reduction percentage?")
            questions.append("Are there any licenses you definitely want to keep?")
        
        elif intent.category == IntentCategory.COMPARISON:
            if len(intent.entities.get("licenses", [])) < 2:
                questions.append("Which licenses would you like me to compare?")
        
        return questions
    
    async def enhance_response_with_genai(self, response: str, context: Dict[str, Any]) -> str:
        """Enhance response using Gen AI"""
        
        try:
            genai_result = await self.genai_service.process_with_genai(
                message=f"Enhance this response to be more helpful and engaging: {response}",
                context=context,
                task_type="response_generation"
            )
            
            if genai_result["success"]:
                return genai_result["response"]
        except Exception as e:
            print(f"Gen AI response enhancement failed: {e}")
        
        return response
    
    def get_processing_capabilities(self) -> Dict[str, Any]:
        """Get information about processing capabilities"""
        
        return {
            "genai_available": bool(self.genai_service.openai_api_key),
            "genai_models": self.genai_service.get_available_models(),
            "fallback_available": True,
            "supported_intents": [category.value for category in IntentCategory],
            "supported_actions": [action.value for action in IntentAction]
        }

