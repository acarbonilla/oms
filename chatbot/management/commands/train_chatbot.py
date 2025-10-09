"""
Django management command to train the AI chatbot
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json
import os

from chatbot.training_service import training_service


class Command(BaseCommand):
    help = 'Train the AI chatbot with conversation data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days back to collect conversation data (default: 30)'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            help='Custom output directory for the trained model'
        )
        parser.add_argument(
            '--collect-only',
            action='store_true',
            help='Only collect training data without training'
        )
        parser.add_argument(
            '--evaluate-only',
            type=str,
            help='Only evaluate an existing model (provide model path)'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show training statistics'
        )

    def handle(self, *args, **options):
        try:
            if options['stats']:
                self.show_statistics()
                return
            
            if options['evaluate_only']:
                self.evaluate_model(options['evaluate_only'])
                return
            
            if options['collect_only']:
                self.collect_data_only(options['days'])
                return
            
            # Full training process
            self.stdout.write("Starting AI chatbot training process...")
            
            # Step 1: Collect conversation data
            self.stdout.write("Step 1: Collecting conversation data...")
            conversation_data = training_service.collect_conversation_data(options['days'])
            
            if not conversation_data:
                raise CommandError("No conversation data found. Start using the chatbot first!")
            
            self.stdout.write(
                self.style.SUCCESS(f"Collected {len(conversation_data)} conversation examples")
            )
            
            # Step 2: Save training data
            self.stdout.write("Step 2: Saving training data...")
            data_file = training_service.save_training_data(conversation_data)
            self.stdout.write(self.style.SUCCESS(f"Training data saved to: {data_file}"))
            
            # Step 3: Create training dataset
            self.stdout.write("Step 3: Creating training dataset...")
            dataset = training_service.create_training_dataset(conversation_data)
            self.stdout.write(self.style.SUCCESS(f"Created dataset with {len(dataset)} examples"))
            
            # Step 4: Fine-tune model
            self.stdout.write("Step 4: Fine-tuning model...")
            model_path = training_service.fine_tune_model(dataset, options.get('output_dir'))
            self.stdout.write(self.style.SUCCESS(f"Model trained and saved to: {model_path}"))
            
            # Step 5: Evaluate model
            self.stdout.write("Step 5: Evaluating model performance...")
            evaluation_results = training_service.evaluate_model_performance(model_path)
            
            avg_score = evaluation_results['average_quality_score']
            self.stdout.write(
                self.style.SUCCESS(f"Model evaluation complete. Average quality score: {avg_score:.3f}")
            )
            
            # Show sample results
            self.stdout.write("\nSample test results:")
            for result in evaluation_results['test_results'][:3]:
                self.stdout.write(f"Query: {result['query']}")
                self.stdout.write(f"Response: {result['response'][:100]}...")
                self.stdout.write(f"Quality: {result['quality_score']:.3f}\n")
            
            self.stdout.write(
                self.style.SUCCESS("AI chatbot training completed successfully!")
            )
            
        except Exception as e:
            raise CommandError(f"Training failed: {str(e)}")

    def show_statistics(self):
        """Show training statistics"""
        stats = training_service.get_training_statistics()
        
        self.stdout.write("AI Chatbot Training Statistics:")
        self.stdout.write("=" * 40)
        self.stdout.write(f"Total Sessions: {stats['total_sessions']}")
        self.stdout.write(f"Total Messages: {stats['total_messages']}")
        self.stdout.write(f"Recent Conversations (7 days): {stats['recent_conversations']}")
        self.stdout.write(f"Average Response Quality: {stats['average_response_quality']}")
        self.stdout.write(f"Training Data Files: {stats['training_data_files']}")
        self.stdout.write(f"Available Models: {stats['available_models']}")
        
        if stats['average_response_quality'] > 0.7:
            self.stdout.write(self.style.SUCCESS("Good response quality"))
        elif stats['average_response_quality'] > 0.5:
            self.stdout.write(self.style.WARNING("Moderate response quality - consider training"))
        else:
            self.stdout.write(self.style.ERROR("Poor response quality - training recommended"))

    def evaluate_model(self, model_path):
        """Evaluate an existing model"""
        if not os.path.exists(model_path):
            raise CommandError(f"Model path does not exist: {model_path}")
        
        self.stdout.write(f"Evaluating model: {model_path}")
        results = training_service.evaluate_model_performance(model_path)
        
        avg_score = results['average_quality_score']
        self.stdout.write(f"Average quality score: {avg_score:.3f}")
        
        self.stdout.write("\nTest Results:")
        for result in results['test_results']:
            self.stdout.write(f"Query: {result['query']}")
            self.stdout.write(f"Response: {result['response'][:100]}...")
            self.stdout.write(f"Quality: {result['quality_score']:.3f}\n")

    def collect_data_only(self, days):
        """Only collect training data without training"""
        self.stdout.write(f"Collecting conversation data from last {days} days...")
        
        conversation_data = training_service.collect_conversation_data(days)
        
        if not conversation_data:
            self.stdout.write(self.style.WARNING("No conversation data found"))
            return
        
        # Save the data
        data_file = training_service.save_training_data(conversation_data)
        
        self.stdout.write(
            self.style.SUCCESS(f"Collected {len(conversation_data)} examples")
        )
        self.stdout.write(f"Data saved to: {data_file}")
        
        # Show quality distribution
        quality_scores = [d['quality_score'] for d in conversation_data]
        high_quality = len([s for s in quality_scores if s >= 0.7])
        medium_quality = len([s for s in quality_scores if 0.5 <= s < 0.7])
        low_quality = len([s for s in quality_scores if s < 0.5])
        
        self.stdout.write(f"High quality responses: {high_quality}")
        self.stdout.write(f"Medium quality responses: {medium_quality}")
        self.stdout.write(f"Low quality responses: {low_quality}")
