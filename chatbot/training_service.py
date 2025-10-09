"""
AI Training Service for OMS Chatbot
Handles model fine-tuning, data collection, and performance tracking
"""

import os
import json
import torch
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Q
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TrainingArguments, Trainer, DataCollatorForLanguageModeling,
    EarlyStoppingCallback
)
from datasets import Dataset
import logging

from .models import ChatSession, ChatMessage, ChatbotConfiguration
from .knowledge_base import OMS_KNOWLEDGE_BASE

logger = logging.getLogger(__name__)

class ChatbotTrainingService:
    """Service for training and improving the AI chatbot"""
    
    def __init__(self):
        self.model_name = "microsoft/DialoGPT-medium"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.training_data_path = os.path.join(settings.BASE_DIR, 'chatbot', 'training_data')
        self.models_path = os.path.join(settings.BASE_DIR, 'chatbot', 'trained_models')
        
        # Create directories if they don't exist
        os.makedirs(self.training_data_path, exist_ok=True)
        os.makedirs(self.models_path, exist_ok=True)
        
        self.tokenizer = None
        self.model = None
        
    def collect_conversation_data(self, days_back: int = 30) -> List[Dict]:
        """Collect conversation data from the database for training"""
        cutoff_date = timezone.now() - timedelta(days=days_back)
        
        # Get all conversations from the last N days
        sessions = ChatSession.objects.filter(
            created_at__gte=cutoff_date
        ).prefetch_related('messages')
        
        training_data = []
        
        for session in sessions:
            messages = session.messages.all().order_by('timestamp')
            
            # Get user groups and region from the user
            user_groups = list(session.user.groups.values_list('name', flat=True))
            region = self._get_user_region(user_groups)
            
            # Group messages into conversation pairs
            user_message = None
            for message in messages:
                if message.message_type == 'user':
                    user_message = message.content
                elif message.message_type == 'bot' and user_message:
                    # Create training example
                    training_example = {
                        'user_message': user_message,
                        'bot_response': message.content,
                        'user_groups': user_groups,
                        'region': region,
                        'session_id': session.id,
                        'timestamp': message.timestamp.isoformat(),
                        'quality_score': self._calculate_response_quality(user_message, message.content)
                    }
                    training_data.append(training_example)
                    user_message = None  # Reset for next pair
        
        return training_data
    
    def _get_user_region(self, user_groups: List[str]) -> str:
        """Determine user's region based on groups"""
        for group in user_groups:
            if '_D' in group:
                return 'Danao'
            elif '_M' in group:
                return 'Mindanao'
            elif any(g in group for g in ['AM', 'EMP', 'EV']) and not any(suffix in group for suffix in ['_D', '_M']):
                return 'C2'
        return 'C2'  # Default to C2
    
    def _calculate_response_quality(self, user_message: str, bot_response: str) -> float:
        """Calculate quality score for a bot response (0-1 scale)"""
        score = 0.0
        
        # Length appropriateness (not too short, not too long)
        if 10 <= len(bot_response) <= 500:
            score += 0.3
        
        # Contains relevant keywords from user message
        user_words = set(user_message.lower().split())
        bot_words = set(bot_response.lower().split())
        if user_words.intersection(bot_words):
            score += 0.2
        
        # Contains OMS-specific terms
        oms_terms = ['facility', 'activity', 'qr', 'technical', 'assessment', 'region']
        if any(term in bot_response.lower() for term in oms_terms):
            score += 0.2
        
        # Not just generic responses
        generic_responses = ['i understand', 'let me help', 'i can assist']
        if not any(phrase in bot_response.lower() for phrase in generic_responses):
            score += 0.2
        
        # Contains actionable information
        if any(word in bot_response.lower() for word in ['statistics', 'data', 'information', 'details']):
            score += 0.1
        
        return min(score, 1.0)
    
    def create_training_dataset(self, conversation_data: List[Dict]) -> Dataset:
        """Create a Hugging Face Dataset from conversation data"""
        
        # Filter high-quality conversations
        quality_data = [d for d in conversation_data if d['quality_score'] >= 0.5]
        
        # Create training examples in DialoGPT format
        training_examples = []
        
        for data in quality_data:
            # Format for DialoGPT: "user: message bot: response"
            formatted_text = f"user: {data['user_message']} bot: {data['bot_response']}"
            
            training_examples.append({
                'text': formatted_text,
                'user_groups': data['user_groups'],
                'region': data['region'],
                'quality_score': data['quality_score']
            })
        
        # Add OMS-specific training examples
        oms_examples = self._create_oms_training_examples()
        training_examples.extend(oms_examples)
        
        return Dataset.from_list(training_examples)
    
    def _create_oms_training_examples(self) -> List[Dict]:
        """Create OMS-specific training examples"""
        examples = []
        
        # Facility management examples
        examples.extend([
            {
                'text': 'user: How do I generate a QR code for a facility? bot: To generate a QR code for a facility, go to Facility Management → Generate QR Code. Select the facility and click Generate. The QR code will contain facility information and can be printed for physical placement.',
                'user_groups': ['AM', 'EMP'],
                'region': 'C2',
                'quality_score': 1.0
            },
            {
                'text': 'user: What facilities are in my region? bot: I can show you a list of facilities in your region. Let me get the current facility data for you.',
                'user_groups': ['AM'],
                'region': 'Danao',
                'quality_score': 0.9
            }
        ])
        
        # Technical activities examples
        examples.extend([
            {
                'text': 'user: How do I upload technical activity images? bot: To upload technical activity images, go to Technical Activities → Add New Activity. Fill in the activity details, then click "Add Images" to upload photos. You can upload multiple images for documentation.',
                'user_groups': ['EMP', 'EV'],
                'region': 'Mindanao',
                'quality_score': 1.0
            },
            {
                'text': 'user: What activities need attention? bot: Let me check for activities that need attention in your region. I can show you high-priority activities or those pending remarks.',
                'user_groups': ['AM'],
                'region': 'C2',
                'quality_score': 0.9
            }
        ])
        
        # Quality assessment examples
        examples.extend([
            {
                'text': 'user: How do I conduct a quality assessment? bot: To conduct a quality assessment, go to Quality Assessment → New Evaluation. Select the facility or activity to assess, fill in the evaluation criteria, and submit your assessment.',
                'user_groups': ['EV'],
                'region': 'Danao',
                'quality_score': 1.0
            }
        ])
        
        return examples
    
    def fine_tune_model(self, dataset: Dataset, output_dir: str = None) -> str:
        """Fine-tune the DialoGPT model with the training data"""
        
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(self.models_path, f"oms_chatbot_{timestamp}")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        
        # Tokenize the dataset
        def tokenize_function(examples):
            return self.tokenizer(
                examples['text'],
                truncation=True,
                padding=True,
                max_length=256,
                return_tensors="pt"
            )
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        # Split into train and validation
        train_test = tokenized_dataset.train_test_split(test_size=0.1)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=10,
            evaluation_strategy="steps",
            eval_steps=100,
            save_strategy="steps",
            save_steps=100,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            report_to=None,  # Disable wandb/tensorboard
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_test['train'],
            eval_dataset=train_test['test'],
            data_collator=data_collator,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )
        
        # Train the model
        logger.info("Starting model fine-tuning...")
        trainer.train()
        
        # Save the fine-tuned model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        logger.info(f"Fine-tuned model saved to: {output_dir}")
        
        return output_dir
    
    def evaluate_model_performance(self, model_path: str) -> Dict:
        """Evaluate the performance of a trained model"""
        
        # Load the trained model
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(model_path)
        
        # Test with sample OMS queries
        test_queries = [
            "How do I generate a QR code?",
            "What facilities are in my region?",
            "Show me activity statistics",
            "How do I upload technical images?",
            "What can you help me with?"
        ]
        
        results = {
            'model_path': model_path,
            'evaluation_date': datetime.now().isoformat(),
            'test_results': []
        }
        
        for query in test_queries:
            # Generate response
            inputs = tokenizer.encode(f"user: {query} bot:", return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 50,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.split("bot:")[-1].strip()
            
            # Evaluate response quality
            quality_score = self._calculate_response_quality(query, response)
            
            results['test_results'].append({
                'query': query,
                'response': response,
                'quality_score': quality_score
            })
        
        # Calculate average performance
        avg_score = np.mean([r['quality_score'] for r in results['test_results']])
        results['average_quality_score'] = avg_score
        
        # Save evaluation results
        eval_file = os.path.join(model_path, 'evaluation_results.json')
        with open(eval_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def get_training_statistics(self) -> Dict:
        """Get statistics about training data and model performance"""
        
        # Get conversation data statistics
        total_sessions = ChatSession.objects.count()
        total_messages = ChatMessage.objects.count()
        
        # Get recent conversation quality
        recent_data = self.collect_conversation_data(days_back=7)
        avg_quality = np.mean([d['quality_score'] for d in recent_data]) if recent_data else 0
        
        # Get training data statistics
        training_files = [f for f in os.listdir(self.training_data_path) if f.endswith('.json')]
        
        return {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'recent_conversations': len(recent_data),
            'average_response_quality': round(avg_quality, 3),
            'training_data_files': len(training_files),
            'available_models': len([d for d in os.listdir(self.models_path) if os.path.isdir(os.path.join(self.models_path, d))])
        }
    
    def save_training_data(self, conversation_data: List[Dict], filename: str = None) -> str:
        """Save conversation data to a file for future training"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"training_data_{timestamp}.json"
        
        filepath = os.path.join(self.training_data_path, filename)
        
        with open(filepath, 'w') as f:
            json.dump(conversation_data, f, indent=2)
        
        logger.info(f"Training data saved to: {filepath}")
        return filepath

# Global training service instance
training_service = ChatbotTrainingService()
