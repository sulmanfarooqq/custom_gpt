# Custom GPT Chatbot

A beautiful CLI-based chatbot powered by Google's Gemini API with a knowledge base of documents.

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

2. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/)

3. Run the chatbot:
   ```bash
   python main.py
   ```

4. Use the menu to configure your API key

## Usage

1. Place your documents in the `knowledge` folder
2. Run the chatbot:
   ```bash
   python main.py
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
- Modify `main.py` to adjust the retrieval logic or add new features
- Add more document processing functions for additional file types

## Troubleshooting

If you encounter the "models/gemini-pro is not found" error:
1. Ensure you're using a recent version of the `google-generativeai` package
2. Check that your API key is valid and properly configured
3. The application now uses `gemini-1.5-flash` which is more widely available