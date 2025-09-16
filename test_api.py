import requests
import json

class MistralAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def chat_completion(self, messages, model="mistral-small-latest", temperature=0.7, max_tokens=1000):
        """
        Send a chat completion request to Mistral AI API
        
        Args:
            messages (list): List of message dictionaries with 'role' and 'content'
            model (str): Model to use (default: mistral-small-latest)
            temperature (float): Controls randomness (0.0 to 1.0)
            max_tokens (int): Maximum number of tokens to generate
            
        Returns:
            dict: API response
        """
        endpoint = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
            "top_p": 1.0
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            if response.status_code == 401:
                print("Authentication Error: Please check your API key")
                print("Response:", response.text)
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response text: {e.response.text}")
            return None

    def list_models(self):
        """
        Get list of available models
        
        Returns:
            dict: API response with available models
        """
        endpoint = f"{self.base_url}/models"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching models: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response text: {e.response.text}")
            return None

def main():
    # Initialize the MistralAI client with your API key
    api_key = "CMpytMlUWyRIcztTKKNazty9nwggKzrm"
    mistral = MistralAI(api_key)
    
    # Initialize conversation history
    conversation_history = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]
    
    print("Welcome to the Mistral AI Chat!")
    print("Type 'quit' or 'exit' to end the conversation")
    print("Type 'clear' to start a new conversation")
    print("-" * 50)
    
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        # Check for exit commands
        if user_input.lower() in ['quit', 'exit']:
            print("\nGoodbye!")
            break
            
        # Check for clear command
        if user_input.lower() == 'clear':
            conversation_history = [
                {"role": "system", "content": "You are a helpful AI assistant."}
            ]
            print("\nConversation history cleared!")
            continue
            
        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": user_input})
        
        # Get response from AI
        print("\nAI is thinking...")
        response = mistral.chat_completion(
            messages=conversation_history,
            model="mistral-small-latest",
            temperature=0.7,
            max_tokens=1000
        )
        
        if response and 'choices' in response:
            # Extract the AI's response
            ai_message = response['choices'][0]['message']['content']
            print(f"\nAI: {ai_message}")
            
            # Add AI's response to conversation history
            conversation_history.append({"role": "assistant", "content": ai_message})
        else:
            print("\nError: Could not get a response from the AI.")

if __name__ == "__main__":
    main() 