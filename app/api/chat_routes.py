from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse
from typing import List, Optional
import uuid

from ..models.chat_models import ChatRequest, ChatResponse, ChatHistory, ConversationContext
from ..services.conversational_agent import ConversationalAgent
from ..services.genai_service import GenAIService

router = APIRouter()

# Initialize the conversational agent
conversational_agent = ConversationalAgent()
genai_service = GenAIService()


@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with Gen AI capabilities"""
    try:
        response = await conversational_agent.process_message(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing enhanced chat request: {str(e)}")


@router.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        history = conversational_agent.get_chat_history(session_id)
        if not history:
            raise HTTPException(status_code=404, detail="Chat history not found")
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving enhanced chat history: {str(e)}")


@router.get("/api/chat/context/{user_id}/{session_id}")
async def get_conversation_context(user_id: str, session_id: str):
    """Get conversation context for a user session"""
    try:
        context = conversational_agent.get_conversation_context(user_id, session_id)
        if not context:
            raise HTTPException(status_code=404, detail="Conversation context not found")
        return context
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving enhanced conversation context: {str(e)}")


@router.post("/api/chat/export/{session_id}")
async def export_chat_session(session_id: str, format: str = "json"):
    """Export chat session as a report"""
    try:
        history = conversational_agent.get_chat_history(session_id)
        if not history:
            raise HTTPException(status_code=404, detail="Chat history not found")
        
        if format == "json":
            return {
                "session_id": session_id,
                "exported_at": history.updated_at.isoformat(),
                "total_messages": len(history.messages),
                "agent_capabilities": conversational_agent.get_agent_capabilities(),
                "conversation": [
                    {
                        "timestamp": msg.timestamp.isoformat(),
                        "user_message": msg.message,
                        "intent": msg.intent.value if msg.intent else None,
                        "action": msg.action.value if msg.action else None,
                        "entities": msg.entities,
                        "ai_response": resp.message,
                        "response_type": resp.response_type,
                        "confidence": resp.confidence,
                        "suggestions": resp.suggestions,
                        "follow_up_questions": resp.follow_up_questions
                    }
                    for msg, resp in zip(history.messages, history.responses)
                ]
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting enhanced chat session: {str(e)}")


@router.get("/api/chat/suggestions")
async def get_chat_suggestions():
    """Get conversation starters with Gen AI capabilities"""
    
    # Get Gen AI model status
    model_status = genai_service.get_model_status()
    
    return {
        "genai_available": model_status["openai_configured"],
        "available_models": model_status["available_models"],
        "suggestions": [
            {
                "category": "Dashboard & Overview",
                "examples": [
                    "Show me the dashboard",
                    "What's our current license status?",
                    "Give me an overview of our software costs"
                ]
            },
            {
                "category": "Advanced Reports",
                "examples": [
                    "Generate an AP team report",
                    "Create a procurement report for Q4",
                    "Show me an executive summary",
                    "Generate a detailed cost analysis report"
                ]
            },
            {
                "category": "AI-Powered Analysis",
                "examples": [
                    "Analyze our license utilization trends",
                    "What are the cost patterns for the last quarter?",
                    "Show me usage analysis for Salesforce",
                    "Identify anomalies in our license usage"
                ]
            },
            {
                "category": "Smart Recommendations",
                "examples": [
                    "What licenses should we cancel to save money?",
                    "Give me cost optimization recommendations",
                    "Which licenses are underutilized?",
                    "Suggest ways to reduce our software spend"
                ]
            },
            {
                "category": "Predictive Forecasting",
                "examples": [
                    "Predict our software costs for next quarter",
                    "What will our usage look like in 6 months?",
                    "Forecast license utilization trends",
                    "Project our budget needs for next year"
                ]
            },
            {
                "category": "Intelligent Comparisons",
                "examples": [
                    "Compare Zoom and Slack usage",
                    "Which vendor gives us the best value?",
                    "Compare costs across different licenses",
                    "Analyze vendor performance metrics"
                ]
            },
            {
                "category": "Natural Language Queries",
                "examples": [
                    "I need to cut costs by 20%, what should I do?",
                    "Our CFO wants a summary for the board meeting",
                    "Help me understand why our costs are increasing",
                    "What's the best way to optimize our license portfolio?"
                ]
            }
        ]
    }


@router.get("/api/chat/capabilities")
async def get_capabilities():
    """Get information about chat capabilities"""
    
    return {
        "agent_capabilities": conversational_agent.get_agent_capabilities(),
        "genai_status": genai_service.get_model_status(),
        "features": [
            "Advanced intent recognition with Gen AI",
            "Natural language understanding",
            "Context-aware conversations",
            "Intelligent response generation",
            "Multi-modal responses (text + visualizations)",
            "Personalized recommendations",
            "Advanced analysis capabilities",
            "Export and reporting features"
        ]
    }


@router.post("/api/chat/analyze")
async def analysis_endpoint(
    analysis_type: str = Query(..., description="Type of analysis to perform"),
    data: dict = None,
    user_id: str = "default_user"
):
    """Perform analysis using Gen AI"""
    
    try:
        if not data:
            raise HTTPException(status_code=400, detail="Analysis data is required")
        
        result = await genai_service.analyze_with_genai(data, analysis_type)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing enhanced analysis: {str(e)}")


@router.post("/api/chat/generate-report")
async def report_generation_endpoint(
    report_type: str = Query(..., description="Type of report to generate"),
    team: str = Query("general", description="Team perspective (ap, procurement, executive, general)"),
    data: dict = None,
    user_id: str = "default_user"
):
    """Generate reports using Gen AI"""
    
    try:
        if not data:
            raise HTTPException(status_code=400, detail="Report data is required")
        
        report = await genai_service.generate_report_with_genai(data, report_type, team)
        return {
            "report": report,
            "report_type": report_type,
            "team": team,
            "generated_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating enhanced report: {str(e)}")


@router.get("/chat", response_class=HTMLResponse)
async def chat_interface():
    """Chat interface with Gen AI capabilities"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI License Assistant - Chat</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body class="bg-gray-100 h-screen">
        <div class="flex h-full">
            <!-- Sidebar -->
            <div class="w-1/4 bg-white shadow-lg p-4">
                <h2 class="text-xl font-bold text-gray-800 mb-4">🤖 AI License Assistant</h2>
                
                <!-- Gen AI Status -->
                <div class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <div class="flex items-center">
                        <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                        <span class="text-sm font-medium text-green-800">OpenAI Powered</span>
                    </div>
                    <p class="text-xs text-green-600 mt-1">Advanced AI models active</p>
                </div>
                
                <!-- Quick Actions -->
                <div class="mb-6">
                    <h3 class="text-sm font-semibold text-gray-600 mb-2">Quick Actions</h3>
                    <div class="space-y-2">
                        <button onclick="sendQuickMessage('Show me the dashboard')" 
                                class="w-full text-left p-2 bg-blue-50 hover:bg-blue-100 rounded text-sm">
                            📊 Dashboard
                        </button>
                        <button onclick="sendQuickMessage('Generate an AP team report')" 
                                class="w-full text-left p-2 bg-green-50 hover:bg-green-100 rounded text-sm">
                            📋 AP Report
                        </button>
                        <button onclick="sendQuickMessage('What are the cost optimization opportunities?')" 
                                class="w-full text-left p-2 bg-yellow-50 hover:bg-yellow-100 rounded text-sm">
                            💡 Recommendations
                        </button>
                        <button onclick="sendQuickMessage('Analyze license utilization trends')" 
                                class="w-full text-left p-2 bg-purple-50 hover:bg-purple-100 rounded text-sm">
                            🔍 Analysis
                        </button>
                        <button onclick="sendQuickMessage('I need to cut costs by 20%, what should I do?')" 
                                class="w-full text-left p-2 bg-red-50 hover:bg-red-100 rounded text-sm">
                            🎯 Cost Optimization
                        </button>
                    </div>
                </div>
                
                <!-- Session Info -->
                <div class="mb-6">
                    <h3 class="text-sm font-semibold text-gray-600 mb-2">Session</h3>
                    <p class="text-xs text-gray-500">Session ID: <span id="session-id">-</span></p>
                    <div class="flex space-x-2 mt-2">
                        <button onclick="exportChat()" class="text-xs bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded">
                            Export Chat
                        </button>
                        <button onclick="showCapabilities()" class="text-xs bg-blue-200 hover:bg-blue-300 px-2 py-1 rounded">
                            Capabilities
                        </button>
                    </div>
                </div>
                
                <!-- Suggestions -->
                <div>
                    <h3 class="text-sm font-semibold text-gray-600 mb-2">Try asking:</h3>
                    <div class="space-y-1 text-xs text-gray-600">
                        <p>• "I need to cut costs by 20%"</p>
                        <p>• "Our CFO wants a board summary"</p>
                        <p>• "Why are our costs increasing?"</p>
                        <p>• "Optimize our license portfolio"</p>
                        <p>• "Predict next quarter costs"</p>
                    </div>
                </div>
            </div>
            
            <!-- Main Chat Area -->
            <div class="flex-1 flex flex-col">
                <!-- Chat Messages -->
                <div id="chat-messages" class="flex-1 overflow-y-auto p-4 space-y-4">
                    <div class="flex justify-center">
                        <div class="bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 px-4 py-2 rounded-lg">
                            🤖 Hi! I'm your AI License Assistant powered by OpenAI. I can understand natural language, provide intelligent analysis, and generate personalized insights about your software licenses. How can I help you today?
                        </div>
                    </div>
                </div>
                
                <!-- Chat Input -->
                <div class="border-t bg-white p-4">
                    <div class="flex space-x-2">
                        <input type="text" id="message-input" 
                               placeholder="Ask me anything about your software licenses in natural language..."
                               class="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                               onkeypress="handleKeyPress(event)">
                        <button onclick="sendMessage()" 
                                class="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-purple-600">
                            Send
                        </button>
                    </div>
                    <div class="mt-2 text-xs text-gray-500">
                        💡 Try natural language queries like "I need to reduce costs" or "Generate a report for our CFO"
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Capabilities Modal -->
        <div id="capabilities-modal" class="fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center z-50">
            <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-semibold">AI Capabilities</h3>
                    <button onclick="hideCapabilities()" class="text-gray-500 hover:text-gray-700">✕</button>
                </div>
                <div id="capabilities-content">
                    <div class="text-center py-4">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                        <p class="text-sm text-gray-500 mt-2">Loading capabilities...</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let sessionId = generateSessionId();
            document.getElementById('session-id').textContent = sessionId.substring(0, 8) + '...';
            
            function generateSessionId() {
                return 'session_' + Math.random().toString(36).substr(2, 9);
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
            
            function sendQuickMessage(message) {
                document.getElementById('message-input').value = message;
                sendMessage();
            }
            
            async function sendMessage() {
                const input = document.getElementById('message-input');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Add user message to chat
                addMessage(message, 'user');
                input.value = '';
                
                // Show typing indicator
                const typingId = addTypingIndicator();
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            user_id: 'default_user',
                            session_id: sessionId
                        })
                    });
                    
                    const data = await response.json();
                    
                    // Remove typing indicator
                    removeTypingIndicator(typingId);
                    
                    // Add AI response
                    addMessage(data.message, 'ai', data);
                    
                    // Handle suggestions
                    if (data.suggestions && data.suggestions.length > 0) {
                        addSuggestions(data.suggestions);
                    }
                    
                    // Handle follow-up questions
                    if (data.follow_up_questions && data.follow_up_questions.length > 0) {
                        addFollowUpQuestions(data.follow_up_questions);
                    }
                    
                    // Handle visualizations
                    if (data.visualizations && data.visualizations.length > 0) {
                        addVisualizations(data.visualizations);
                    }
                    
                } catch (error) {
                    removeTypingIndicator(typingId);
                    addMessage('Sorry, I encountered an error. Please try again.', 'ai');
                    console.error('Error:', error);
                }
            }
            
            function addMessage(message, sender, data = null) {
                const chatMessages = document.getElementById('chat-messages');
                const messageDiv = document.createElement('div');
                
                if (sender === 'user') {
                    messageDiv.className = 'flex justify-end';
                    messageDiv.innerHTML = `
                        <div class="bg-blue-500 text-white px-4 py-2 rounded-lg max-w-xs">
                            ${message}
                        </div>
                    `;
                } else {
                    messageDiv.className = 'flex justify-start';
                    messageDiv.innerHTML = `
                        <div class="bg-white border px-4 py-2 rounded-lg max-w-2xl">
                            <div class="whitespace-pre-wrap">${message}</div>
                            ${data && data.confidence ? `<div class="text-xs text-gray-500 mt-1">Confidence: ${(data.confidence * 100).toFixed(1)}%</div>` : ''}
                        </div>
                    `;
                }
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function addTypingIndicator() {
                const chatMessages = document.getElementById('chat-messages');
                const typingDiv = document.createElement('div');
                typingDiv.id = 'typing-indicator';
                typingDiv.className = 'flex justify-start';
                typingDiv.innerHTML = `
                    <div class="bg-gray-200 px-4 py-2 rounded-lg">
                        <div class="flex space-x-1">
                            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                        </div>
                    </div>
                `;
                chatMessages.appendChild(typingDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
                return 'typing-indicator';
            }
            
            function removeTypingIndicator(id) {
                const typingDiv = document.getElementById(id);
                if (typingDiv) {
                    typingDiv.remove();
                }
            }
            
            function addSuggestions(suggestions) {
                const chatMessages = document.getElementById('chat-messages');
                const suggestionsDiv = document.createElement('div');
                suggestionsDiv.className = 'flex justify-start';
                
                let suggestionsHTML = '<div class="bg-gray-50 border px-4 py-2 rounded-lg max-w-2xl"><div class="text-sm text-gray-600 mb-2">💡 Suggestions:</div><div class="space-y-1">';
                
                suggestions.forEach(suggestion => {
                    suggestionsHTML += `
                        <button onclick="sendQuickMessage('${suggestion}')" 
                                class="block w-full text-left text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 px-2 py-1 rounded">
                            ${suggestion}
                        </button>
                    `;
                });
                
                suggestionsHTML += '</div></div>';
                suggestionsDiv.innerHTML = suggestionsHTML;
                chatMessages.appendChild(suggestionsDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function addFollowUpQuestions(questions) {
                const chatMessages = document.getElementById('chat-messages');
                const questionsDiv = document.createElement('div');
                questionsDiv.className = 'flex justify-start';
                
                let questionsHTML = '<div class="bg-blue-50 border border-blue-200 px-4 py-2 rounded-lg max-w-2xl"><div class="text-sm text-blue-600 mb-2">❓ Follow-up Questions:</div><div class="space-y-1">';
                
                questions.forEach(question => {
                    questionsHTML += `
                        <button onclick="sendQuickMessage('${question}')" 
                                class="block w-full text-left text-sm text-blue-700 hover:text-blue-900 hover:bg-blue-100 px-2 py-1 rounded">
                            ${question}
                        </button>
                    `;
                });
                
                questionsHTML += '</div></div>';
                questionsDiv.innerHTML = questionsHTML;
                chatMessages.appendChild(questionsDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function addVisualizations(visualizations) {
                const chatMessages = document.getElementById('chat-messages');
                
                visualizations.forEach((viz, index) => {
                    const vizDiv = document.createElement('div');
                    vizDiv.className = 'flex justify-start';
                    vizDiv.innerHTML = `
                        <div class="bg-white border px-4 py-2 rounded-lg max-w-2xl">
                            <div class="text-sm font-semibold mb-2">${viz.title}</div>
                            <div id="chart-${index}" style="width: 100%; height: 300px;"></div>
                        </div>
                    `;
                    chatMessages.appendChild(vizDiv);
                    
                    // Render chart
                    setTimeout(() => {
                        if (viz.type === 'line_chart') {
                            const trace = {
                                x: viz.data.dates,
                                y: viz.data.costs,
                                type: 'scatter',
                                mode: 'lines+markers',
                                name: 'Cost Trend',
                                line: { color: '#3B82F6' }
                            };
                            Plotly.newPlot(`chart-${index}`, [trace], {
                                title: '',
                                xaxis: { title: 'Date' },
                                yaxis: { title: 'Cost ($)' },
                                margin: { t: 30, b: 40, l: 40, r: 20 }
                            }, {responsive: true});
                        } else if (viz.type === 'bar_chart') {
                            const trace = {
                                x: viz.data.ranges,
                                y: viz.data.counts,
                                type: 'bar',
                                name: 'License Count',
                                marker: { color: '#F59E0B' }
                            };
                            Plotly.newPlot(`chart-${index}`, [trace], {
                                title: '',
                                xaxis: { title: 'Utilization Range (%)' },
                                yaxis: { title: 'Number of Licenses' },
                                margin: { t: 30, b: 40, l: 40, r: 20 }
                            }, {responsive: true});
                        }
                    }, 100);
                });
                
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            async function exportChat() {
                try {
                    const response = await fetch(`/api/chat/export/${sessionId}`);
                    const data = await response.json();
                    
                    // Create and download file
                    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `chat_export_${sessionId}.json`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    
                } catch (error) {
                    console.error('Error exporting chat:', error);
                    alert('Error exporting chat. Please try again.');
                }
            }
            
            async function showCapabilities() {
                const modal = document.getElementById('capabilities-modal');
                const content = document.getElementById('capabilities-content');
                
                modal.classList.remove('hidden');
                modal.classList.add('flex');
                
                try {
                    const response = await fetch('/api/chat/capabilities');
                    const data = await response.json();
                    
                    let html = '<div class="space-y-4">';
                    
                    // Gen AI Status
                    html += '<div class="p-3 bg-green-50 border border-green-200 rounded">';
                    html += '<h4 class="font-semibold text-green-800">Gen AI Status</h4>';
                    html += `<p class="text-sm text-green-600">Available: ${data.genai_status.openai_configured ? 'Yes' : 'No'}</p>`;
                    if (data.genai_status.available_models.length > 0) {
                        html += '<p class="text-sm text-green-600">Models: ' + data.genai_status.available_models.map(m => m.model).join(', ') + '</p>';
                    }
                    html += '</div>';
                    
                    // Features
                    html += '<div class="p-3 bg-blue-50 border border-blue-200 rounded">';
                    html += '<h4 class="font-semibold text-blue-800">Features</h4>';
                    html += '<ul class="text-sm text-blue-600 space-y-1">';
                    data.features.forEach(feature => {
                        html += `<li>• ${feature}</li>`;
                    });
                    html += '</ul></div>';
                    
                    // Agent Capabilities
                    html += '<div class="p-3 bg-purple-50 border border-purple-200 rounded">';
                    html += '<h4 class="font-semibold text-purple-800">Agent Capabilities</h4>';
                    html += `<p class="text-sm text-purple-600">Gen AI Available: ${data.agent_capabilities.genai_available ? 'Yes' : 'No'}</p>`;
                    html += `<p class="text-sm text-purple-600">Supported Intents: ${data.agent_capabilities.supported_intents.length}</p>`;
                    html += `<p class="text-sm text-purple-600">Active Sessions: ${data.agent_capabilities.conversation_contexts}</p>`;
                    html += '</div>';
                    
                    html += '</div>';
                    content.innerHTML = html;
                    
                } catch (error) {
                    content.innerHTML = '<div class="text-red-600">Error loading capabilities</div>';
                }
            }
            
            function hideCapabilities() {
                const modal = document.getElementById('capabilities-modal');
                modal.classList.add('hidden');
                modal.classList.remove('flex');
            }
        </script>
    </body>
    </html>
    """

