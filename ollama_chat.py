#!/usr/bin/env python3
"""
Ollama Chat Test Program

This script demonstrates how to use the Ollama Python client to chat with locally running models.
It provides a simple command-line interface for interactive conversations.
"""

import ollama
import sys
import os
from typing import List, Dict, Any


class OllamaChat:
    """A simple chat interface for Ollama models."""
    
    def __init__(self, model_name: str = "qwen3.5:2b"):
        """
        Initialize the chat client.
        
        Args:
            model_name (str): The name of the Ollama model to use
        """
        self.model_name = model_name
        self.client = ollama.Client()
        self.messages: List[Dict[str, str]] = []
        
    def check_model_available(self) -> bool:
        """Check if the specified model is available."""
        try:
            # Try to get model info
            models = self.client.list()
            available_models = []
            
            # Handle the Ollama ListResponse object
            if hasattr(models, 'models'):
                available_models = [model.model for model in models.models]
            elif isinstance(models, dict) and 'models' in models:
                available_models = [model['name'] for model in models['models']]
            elif isinstance(models, list):
                available_models = [model['name'] for model in models]
            else:
                # Fallback: try to extract model names from any iterable
                try:
                    available_models = []
                    for item in models:
                        if hasattr(item, 'model'):
                            available_models.append(item.model)
                        elif isinstance(item, dict) and 'name' in item:
                            available_models.append(item['name'])
                except:
                    pass
            
            if self.model_name in available_models:
                print(f"✓ Model '{self.model_name}' is available")
                return True
            else:
                print(f"✗ Model '{self.model_name}' not found")
                print("Available models:")
                for model in available_models:
                    print(f"  - {model}")
                return False
                
        except Exception as e:
            print(f"Error checking model availability: {e}")
            return False
    
    def chat_stream(self, message: str):
        """
        Send a message to the model and stream the response.
        
        Args:
            message (str): The user's message
        """
        try:
            # Add user message to conversation history
            self.messages.append({
                'role': 'user',
                'content': message
            })
            
            # Get streaming response from model with tool calls enabled
            print("AI: ", end="", flush=True)
            full_response = ""
            tool_calls = []
            
            for chunk in self.client.chat(
                model=self.model_name,
                messages=self.messages,
                stream=True,
                options={
                    'num_ctx': 4096,  # Context window size
                    'num_predict': 2048,  # Max tokens to generate
                    'temperature': 0.7,  # Creativity level
                    'top_p': 0.9,  # Nucleus sampling
                    'repeat_penalty': 1.1,  # Repetition penalty
                }
            ):
                # Handle tool calls (thinking process)
                if 'tool_calls' in chunk and chunk['tool_calls']:
                    for tool_call in chunk['tool_calls']:
                        if tool_call['function']['name'] == 'thinking':
                            thinking_content = tool_call['function']['arguments']
                            print(f"[思考: {thinking_content}]", end="", flush=True)
                
                # Handle regular content
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    full_response += content
                    print(content, end="", flush=True)
            
            print()  # New line after response
            
            # Store the full response in conversation history
            self.messages.append({
                'role': 'assistant',
                'content': full_response
            })
            
            return full_response
            
        except Exception as e:
            print(f"Error during chat: {e}")
            error_msg = "Sorry, I encountered an error while processing your message."
            print(error_msg)
            return error_msg
    
    def clear_history(self):
        """Clear the conversation history."""
        self.messages = []
        print("Conversation history cleared.")
    
    def interactive_chat(self):
        """Start an interactive chat session."""
        print(f"\n=== Ollama Chat with {self.model_name} ===")
        print("Type 'clear' to clear history, 'exit' to quit\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() == 'exit':
                    print("Goodbye!")
                    break
                elif user_input.lower() == 'clear':
                    self.clear_history()
                elif user_input:
                    self.chat_stream(user_input)
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break


def get_available_models(client) -> List[str]:
    """Get list of available models."""
    try:
        models = client.list()
        available_models = []
        
        # Handle the Ollama ListResponse object
        if hasattr(models, 'models'):
            available_models = [model.model for model in models.models]
        elif isinstance(models, dict) and 'models' in models:
            available_models = [model['name'] for model in models['models']]
        elif isinstance(models, list):
            available_models = [model['name'] for model in models]
        else:
            # Fallback: try to extract model names from any iterable
            try:
                for item in models:
                    if hasattr(item, 'model'):
                        available_models.append(item.model)
                    elif isinstance(item, dict) and 'name' in item:
                        available_models.append(item['name'])
            except:
                pass
        
        return available_models
    except Exception as e:
        print(f"Error getting available models: {e}")
        return []


def select_model(client) -> str:
    """Let user select a model from available options."""
    available_models = get_available_models(client)
    
    if not available_models:
        print("No models found. Please make sure Ollama is running and has models installed.")
        sys.exit(1)
    
    print("\nAvailable models:")
    for i, model in enumerate(available_models, 1):
        print(f"  {i}. {model}")
    
    while True:
        try:
            choice = input(f"\nSelect a model (1-{len(available_models)}) or enter model name directly: ").strip()
            
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(available_models):
                    return available_models[index]
                else:
                    print(f"Invalid selection. Please choose a number between 1 and {len(available_models)}.")
            else:
                # User entered a model name directly
                if choice in available_models:
                    return choice
                else:
                    print(f"Model '{choice}' not found. Please select from the available models.")
                    
        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)
        except EOFError:
            print("\nGoodbye!")
            sys.exit(0)


def main():
    """Main function to run the chat program."""
    print("Ollama Chat Test Program")
    print("=" * 40)
    
    # Initialize client to check models
    client = ollama.Client()
    
    # Check if a model name was provided as command line argument
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
    else:
        # Let user select a model
        model_name = select_model(client)
    
    print(f"\nUsing model: {model_name}")
    
    # Initialize chat client
    chat_client = OllamaChat(model_name)
    
    # Check if model is available (this should always pass now, but good to verify)
    if not chat_client.check_model_available():
        print(f"\nError: Model '{model_name}' is not available.")
        sys.exit(1)
    
    # Start interactive chat
    chat_client.interactive_chat()


if __name__ == "__main__":
    main()