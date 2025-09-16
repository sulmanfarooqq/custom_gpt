# Custom GPT Chatbot

A beautiful CLI-based chatbot powered by Mistral AI's API with a knowledge base of documents.

## Features

- Beautiful CLI interface using the `rich` library with panels, colors, and markdown support
- Menu-driven interface with setup and configuration options
- Conversation history tracking for context-aware responses
- Support for multiple document types (PDF, Word, Excel, TXT, Markdown)
- Customizable prompt template
- Retrieval Augmented Generation (RAG) for context-aware responses
- API key management through the interface

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Get a Mistral AI API key from [Mistral AI Platform](https://console.mistral.ai/)

3. Run the chatbot:
   ```bash
   python main_updated.py
   ```

4. Use the menu to configure your API key

## Usage

1. Place your documents in the `knowledge` folder
2. Run the chatbot:
   ```bash
   python main_updated.py
   ```

3. Select option 1 to start chatting
4. Ask questions related to your documents

## Supported File Types

- PDF (.pdf)
- Word Documents (.docx)
- Excel Spreadsheets (.xlsx, .xls)
- Text Files (.txt)
- Markdown Files (.md)

## Commands

While chatting, you can use these commands:
- `/new` - Start a new conversation
- `/exit` - Exit the chat
- `/help` - Show help information

## Customization

- Edit `prompt.txt` to change the AI's behavior and personality
- Modify `main_updated.py` to adjust the retrieval logic or add new features
- Add more document processing functions for additional file types

## Troubleshooting

If you encounter connection issues:
1. Ensure you're using a valid Mistral AI API key
2. Check that your API key is properly configured in the .env file
3. Verify you have internet connectivity
4. Make sure you're using `main_updated.py` which uses the working Mistral AI implementation