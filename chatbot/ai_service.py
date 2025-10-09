import os
from typing import Optional, List, Dict
from django.conf import settings
from groq import Groq
from .knowledge_base import get_contextual_response, OMS_KNOWLEDGE_BASE


class ChatbotAIService:
    """Service class for handling AI chatbot interactions using Groq"""
    
    def __init__(self):
        self.client = None
        self.model_name = "llama-3.3-70b-versatile"  # Fast and efficient Groq model
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Groq API client"""
        try:
            api_key = getattr(settings, 'GROQ_API_KEY', None)
            if not api_key:
                print("Warning: GROQ_API_KEY not found in settings. Please add it to your .env file.")
                self.client = None
                return
            
            self.client = Groq(api_key=api_key)
            print(f"Groq AI client initialized successfully with model: {self.model_name}")
                
        except Exception as e:
            print(f"Error initializing Groq client: {str(e)}")
            self.client = None
    
    def generate_response(
        self, 
        user_message: str, 
        conversation_history: List[Dict] = None, 
        user_context: Dict = None
    ) -> str:
        """Generate AI response to user message with OMS-specific knowledge"""
        
        user_groups = user_context.get('user_groups', []) if user_context else []
        region = user_context.get('region', None) if user_context else None
        
        # Check if this is a conversational/casual message (prioritize natural AI interaction)
        if self._is_conversational(user_message):
            # Use AI for natural conversation - don't check knowledge base for greetings
            if self.client:
                try:
                    messages = self._prepare_messages(user_message, conversation_history, user_context)
                    chat_completion = self.client.chat.completions.create(
                        messages=messages,
                        model=self.model_name,
                        temperature=0.8,  # Higher temperature for more natural responses
                        max_tokens=300,
                        top_p=1,
                        stream=False
                    )
                    bot_response = chat_completion.choices[0].message.content.strip()
                    return self._clean_response(bot_response)
                except Exception as e:
                    print(f"Error generating conversational response: {str(e)}")
                    # Return simple fallback for conversational messages
                    return self._get_simple_conversational_fallback(user_message)
            else:
                # No client, return simple conversational fallback
                return self._get_simple_conversational_fallback(user_message)
        
        # For specific OMS queries, check knowledge base for data-driven responses
        if self._is_data_query(user_message):
            contextual_response = get_contextual_response(user_message, user_groups, region, user_context)
        if len(contextual_response) > 100 and not contextual_response.startswith("I understand you're asking"):
            return contextual_response
        
        # Default: Use AI for interactive responses
        if not self.client:
            return self._get_fallback_response(user_message, user_groups, region)
        
        try:
            # Prepare messages for Groq API
            messages = self._prepare_messages(user_message, conversation_history, user_context)
            
            # Generate response using Groq
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=0.7,
                max_tokens=500,
                top_p=1,
                stream=False
            )
            
            # Extract the response
            bot_response = chat_completion.choices[0].message.content.strip()
            
            # Clean and validate response
            bot_response = self._clean_response(bot_response)
            
            return bot_response if bot_response else self._get_fallback_response(user_message, user_groups, region)
            
        except Exception as e:
            print(f"Error generating Groq AI response: {str(e)}")
            # Return contextual response as fallback
            return get_contextual_response(user_message, user_groups or [], region, user_context)
    
    def _is_conversational(self, message: str) -> bool:
        """Check if message is casual/conversational"""
        casual_patterns = [
            'hi', 'hello', 'hey', 'howdy', 'greetings',
            'good morning', 'good afternoon', 'good evening', 'good night',
            'how are you', 'whats up', "what's up", 'sup',
            'thank', 'thanks', 'thank you', 'thx',
            'bye', 'goodbye', 'see you', 'later',
            'ok', 'okay', 'cool', 'nice', 'great', 'awesome',
            'yes', 'yeah', 'yep', 'yup', 'sure',
            'no', 'nope', 'nah',
        ]
        message_lower = message.lower().strip()
        # Return True if message is very short and matches casual patterns
        return len(message.split()) <= 5 and any(pattern in message_lower for pattern in casual_patterns)
    
    def _is_data_query(self, message: str) -> bool:
        """Check if message is asking for database/statistics or specific OMS features"""
        data_patterns = [
            # Database queries
            'show', 'list', 'count', 'how many', 'statistics', 'stats',
            'search', 'find', 'look for',
            'my activities', 'my uploads', 'my facilities',
            # Feature-specific queries that have pre-loaded answers
            'dashboard', 'main page', 'home page', 'overview',
            'how do i', 'how can i', 'how to', 'where do i',
            'navigate', 'menu', 'where is', 'find page',
            'qr', 'qr code', 'facility code',
            'assessment', 'quality', 'evaluation',
            'activity', 'technical', 'upload',
            'report', 'pdf', 'download', 'export',
            'permission', 'access', 'denied',
            'help', 'tutorial', 'guide', 'instructions'
        ]
        return any(pattern in message.lower() for pattern in data_patterns)
    
    def _prepare_messages(
        self, 
        user_message: str, 
        conversation_history: List[Dict] = None, 
        user_context: Dict = None
    ) -> List[Dict]:
        """Prepare messages array for Groq API"""
        
        # Start with system message
        system_prompt = self._build_system_prompt(user_context)
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        # Add conversation history (last 6 messages for context)
        if conversation_history:
            for msg in conversation_history[-6:]:
                if msg['message_type'] == 'user':
                    messages.append({
                        "role": "user",
                        "content": msg['content']
                    })
                elif msg['message_type'] == 'bot':
                    messages.append({
                        "role": "assistant",
                        "content": msg['content']
                    })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def _build_system_prompt(self, user_context: Dict = None) -> str:
        """Build comprehensive system prompt for OMS Assistant"""
        
        prompt = """You are a friendly and helpful AI assistant for an Operations Management System (OMS). Be conversational and natural in your interactions.

**Your Personality:**
- Warm and approachable - respond naturally to greetings and casual chat
- Clear and concise - keep responses brief unless asked for details
- Helpful and proactive - offer suggestions when appropriate
- Professional yet friendly - balance casual conversation with expertise

**Conversation Style:**
- For greetings like "hi", "hello", "hey" → Respond naturally like a human would
- For "thank you" → Reply warmly and briefly
- For casual chat → Be friendly and engaging
- For specific questions → Provide clear, actionable answers
- Use a conversational tone, avoid being overly formal or robotic

**OMS System You Support:**

**Regions:** C2, Danao, Mindanao

**User Roles:**
- AM (Area Manager) - Full access, can manage everything
- EMP (Employee) - Can log activities and upload images
- EV (Evaluator) - Can conduct quality assessments

**Main Features:**
- **Facility Management:** QR codes, facility tracking, location management
- **Technical Activities:** Activity logging, image uploads, documentation
- **Quality Assessment:** Image comparison, evaluations, reports
- **Reports:** PDF generation, data analysis

**Response Guidelines:**
- Keep initial responses short (1-3 sentences) unless user wants more
- For greetings: Just greet back warmly
- For questions: Provide direct answers with actionable steps
- For complex topics: Offer to elaborate if they want more details
- Be conversational - imagine you're a helpful colleague, not a manual
"""
        
        # Add user-specific context
        if user_context:
            user_groups = user_context.get('user_groups', [])
            region = user_context.get('region', '')
            username = user_context.get('username', 'User')
            
            if user_groups or region:
                prompt += f"\n**Current User:**\n"
                if username:
                    prompt += f"- Name: {username}\n"
                if user_groups:
                    prompt += f"- Role: {', '.join(user_groups)}\n"
                if region:
                    prompt += f"- Region: {region}\n"
        
        prompt += "\n**Remember:** Be natural, friendly, and conversational. You're here to help, not just provide information."
        
        return prompt
    
    def _clean_response(self, response: str) -> str:
        """Clean and format the AI response"""
        # Remove any markdown artifacts if needed
        response = response.strip()
        
        # Ensure response isn't too long
        if len(response) > 800:
            # Try to cut at last sentence before 800 chars
            sentences = response[:800].split('. ')
            if len(sentences) > 1:
                response = '. '.join(sentences[:-1]) + '.'
        else:
                response = response[:800] + "..."
        
        return response
    
    def _get_simple_conversational_fallback(self, user_message: str) -> str:
        """Provide simple natural responses for casual messages when AI is unavailable"""
        message_lower = user_message.lower().strip()
        
        # Greetings
        if any(word in message_lower for word in ['hi', 'hello', 'hey', 'howdy']):
            return "Hello! How can I help you today?"
        elif any(word in message_lower for word in ['good morning']):
            return "Good morning! What can I do for you?"
        elif any(word in message_lower for word in ['good afternoon']):
            return "Good afternoon! How can I assist you?"
        elif any(word in message_lower for word in ['good evening', 'good night']):
            return "Good evening! How may I help you?"
        
        # Thanks
        elif any(word in message_lower for word in ['thank', 'thanks']):
            return "You're welcome! Let me know if you need anything else."
        
        # How are you
        elif 'how are you' in message_lower:
            return "I'm doing great, thanks for asking! How can I help you with your OMS tasks?"
        
        # Goodbye
        elif any(word in message_lower for word in ['bye', 'goodbye', 'see you']):
            return "Goodbye! Feel free to come back if you need anything."
        
        # Affirmations
        elif any(word in message_lower for word in ['ok', 'okay', 'cool', 'nice', 'great', 'awesome']):
            return "Great! Anything else I can help you with?"
        
        # Yes/No
        elif message_lower in ['yes', 'yeah', 'yep', 'yup', 'sure']:
            return "Okay! What would you like to do?"
        elif message_lower in ['no', 'nope', 'nah']:
            return "Alright! Let me know if you need anything."
        
        # Default
        return "I'm here to help! What would you like to know?"
    
    def _get_fallback_response(
        self, 
        user_message: str, 
        user_groups: List[str] = None, 
        region: str = None
    ) -> str:
        """Provide fallback responses when AI model is unavailable"""
        try:
            response = get_contextual_response(user_message, user_groups or [], region)
            if response and len(response.strip()) > 10:
                return response
        except Exception as e:
            print(f"Contextual response error: {str(e)}")
        
        # Ultimate fallback
        return f"I understand you're asking about: '{user_message}'. I'm here to help with OMS operations including facilities, technical activities, quality assessments, and reports. Could you please be more specific about what you need help with?"


# Global instance
ai_service = ChatbotAIService()
