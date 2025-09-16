# -*- coding: utf-8 -*-
import os
import sys
import re
import time
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv, set_key
import colorama
from pwinput import pwinput
import PyPDF2
import docx
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.live import Live

# Initialize Colorama for cross-platform colored output
colorama.init(autoreset=True)

# Initialize Rich console
console = Console()

# --- Configuration ---
API_PROVIDER = "gemini"
MODEL_NAME = "gemini-1.5-flash"
API_KEY_NAME = "GEMINI_API_KEY"
ENV_FILE = ".env"

# UI Colors
class colors:
    TITLE = colorama.Fore.CYAN + colorama.Style.BRIGHT
    PROMPT_BORDER = colorama.Fore.YELLOW
    PROMPT_TEXT = colorama.Fore.WHITE + colorama.Style.BRIGHT
    ASSISTANT_BORDER = colorama.Fore.CYAN
    ASSISTANT_TEXT = colorama.Fore.LIGHTBLUE_EX
    INFO_BORDER = colorama.Fore.GREEN
    WARNING_BORDER = colorama.Fore.YELLOW
    ERROR_BORDER = colorama.Fore.RED
    SYSTEM_TEXT = colorama.Fore.MAGENTA
    RESET = colorama.Style.RESET_ALL

# ASCII Banner for Custom GPT
banner_text = Text("""
  ██████╗██╗   ██╗███████╗████████╗ ██████╗ ███╗   ███╗    ██████╗ ██████╗ ████████╗
 ██╔════╝██║   ██║██╔════╝╚══██╔══╝██╔═══██╗████╗ ████║   ██╔════╝ ██═══██╗╚══██╔══╝
██║     ███████║███████╗   ██║   ██║   ██║██╔████╔██║   ██║  ███╗██████╔╝   ██║   
██║     ██╔══██║╚════██║   ██║   ██║   ██║██║╚██╔╝██║   ██║   ██║██╔════╝   ██║   
╚██████╗██║  ██║███████║   ██║   ╚██████╔╝██║ ╚═╝ ██║   ╚██████╔╝██║        ██║   
 ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝    ╚═════╝ ╚═╝        ╚═╝   
""", style="bold cyan")

# --- File Processing Functions ---
def extract_text_from_pdf(file_path):
    """Extract text from PDF files"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        console.print(f"[red]Error reading PDF {file_path}: {str(e)}[/red]")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from Word documents"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        console.print(f"[red]Error reading DOCX {file_path}: {str(e)}[/red]")
        return ""

def extract_text_from_excel(file_path):
    """Extract text from Excel files"""
    try:
        # Read all sheets
        excel_file = pd.ExcelFile(file_path)
        text = ""
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            text += f"Sheet: {sheet_name}\n"
            text += df.to_string() + "\n\n"
        return text
    except Exception as e:
        console.print(f"[red]Error reading Excel {file_path}: {str(e)}[/red]")
        return ""

def extract_text_from_txt(file_path):
    """Extract text from text files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        console.print(f"[red]Error reading TXT {file_path}: {str(e)}[/red]")
        return ""

def load_knowledge_base():
    """Load all documents from the knowledge folder"""
    knowledge_folder = "knowledge"
    if not os.path.exists(knowledge_folder):
        console.print(Panel("[yellow]Knowledge folder not found[/yellow]", border_style="yellow"))
        return []
    
    documents = []
    supported_extensions = ['.pdf', '.docx', '.xlsx', '.xls', '.txt', '.md']
    
    # Find all files in knowledge folder
    files_processed = 0
    for root, dirs, files in os.walk(knowledge_folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension in supported_extensions:
                console.print(f"[blue]Processing {file_path}...[/blue]")
                
                content = ""
                if file_extension == '.pdf':
                    content = extract_text_from_pdf(file_path)
                elif file_extension == '.docx':
                    content = extract_text_from_docx(file_path)
                elif file_extension in ['.xlsx', '.xls']:
                    content = extract_text_from_excel(file_path)
                elif file_extension in ['.txt', '.md']:
                    content = extract_text_from_txt(file_path)
                
                if content:
                    # Split document into chunks to make retrieval more effective
                    chunks = split_text_into_chunks(content, file_path)
                    documents.extend(chunks)
                    files_processed += 1
    
    console.print(Panel(f"[green]Successfully processed {files_processed} files[/green]", border_style="green"))
    return documents

def split_text_into_chunks(text, source_file, chunk_size=1000, overlap=100):
    """Split text into smaller chunks for better retrieval"""
    chunks = []
    words = text.split()
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk_text = ' '.join(chunk_words)
        
        # Skip very short chunks
        if len(chunk_text.strip()) > 50:
            chunks.append({
                'content': chunk_text,
                'source': source_file
            })
    
    return chunks

def get_relevant_context(documents, question, max_chunks=3):
    """
    Simple context retrieval based on keyword matching.
    In a more advanced version, you might use embedding similarity.
    """
    if not documents:
        return ""
    
    # Convert question to lowercase for case-insensitive matching
    question_lower = question.lower()
    
    # Simple keyword matching to find relevant chunks
    relevant_chunks = []
    for doc in documents:
        # Count matches of question words in the document
        doc_content_lower = doc['content'].lower()
        match_count = sum(1 for word in question_lower.split() if word in doc_content_lower)
        
        if match_count > 0:
            relevant_chunks.append((match_count, doc))
    
    # Sort by match count and take top chunks
    relevant_chunks.sort(key=lambda x: x[0], reverse=True)
    top_chunks = relevant_chunks[:max_chunks]
    
    # Format context with source information
    context_parts = []
    for _, chunk in top_chunks:
        context_parts.append(f"Source: {chunk['source']}\nContent: {chunk['content']}")
    
    return "\n\n---\n\n".join(context_parts) if context_parts else "No relevant context found."

# --- UI Class ---
class UI:
    """Handles all advanced terminal UI using the 'rich' library."""

    def __init__(self):
        self.console = Console()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_banner(self):
        self.clear_screen()
        self.console.print(banner_text, justify="center")
        self.console.rule("[bold green]◈[/bold green]" * 3, style="green")
        info_line = Text("Custom GPT Chatbot with Knowledge Base", style="green")
        self.console.print(info_line, justify="center")
        self.console.print()

    def display_main_menu(self):
        menu_text = Text.from_markup(
            """
[bold yellow][1][/bold yellow] Start Chat with Custom GPT
[bold yellow][2][/bold yellow] Configure API Key
[bold yellow][3][/bold yellow] About
[bold yellow][4][/bold yellow] Exit
"""
        )
        self.console.print(
            Panel(menu_text, title="[bold cyan]Main Menu[/bold cyan]", border_style="cyan", expand=True)
        )

    def display_message(self, title: str, message: str, border_style: str):
        """Displays a static message in a Panel."""
        self.console.print(
            Panel(Text(message, justify="left"), title=f"[bold {border_style}]{title}[/]", border_style=border_style)
        )

    def get_input(self, prompt: str) -> str:
        """Gets user input with a styled prompt."""
        return self.console.input(f"[bold yellow]╚═>[/bold yellow] [bold white]{prompt}:[/bold white] ")

    def display_markdown_message(self, title: str, content_stream):
        """
        Displays a 'typing' animation while collecting a stream, then renders it as Markdown.
        """
        panel_title = f"[bold cyan]{title}[/bold cyan]"
        
        # The Live context will manage the "is typing" animation, then disappear
        with Live(console=self.console, refresh_per_second=10, transient=True) as live:
            live.update(Panel(Text(f"{title} is typing..."), title=panel_title, border_style="dim cyan"))
            
            # Collect the full response from the generator stream
            full_response_md = "".join(list(content_stream))

        # After the Live context is finished, render the final, complete Markdown content
        if full_response_md:
            markdown_content = Markdown(
                full_response_md.strip(),
                style="bright_blue"  # Base style for text outside markdown elements
            )
            self.console.print(Panel(markdown_content, title=panel_title, border_style="cyan"))
        else:
            # Handle cases where the stream was empty or failed
            self.display_message(title, "No response received from the API.", "red")

# --- API Client Class ---
class LLMClient:
    """Handles all communication with the Large Language Model API."""
    
    def __init__(self, api_key: str, ui: UI):
        self.ui = ui
        self.documents = load_knowledge_base()
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name=MODEL_NAME)
        self.chat = self.model.start_chat(history=[])
        
        # Load custom prompt template
        self.custom_prompt = self.load_custom_prompt()
        
        # Send initial context as first message
        if self.documents:
            context_summary = f"Knowledge base loaded with {len(self.documents)} document chunks."
            self.chat.send_message(f"System: {context_summary}")

    def load_custom_prompt(self):
        """Load the custom prompt template from file"""
        try:
            with open("prompt.txt", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            console.print("[yellow]Warning: prompt.txt not found, using default prompt[/yellow]")
            return "You are a helpful AI assistant. Answer the user's question: {question}"

    def clear_history(self):
        self.chat = self.model.start_chat(history=[])
        # Reload documents and send context again
        self.documents = load_knowledge_base()
        if self.documents:
            context_summary = f"Knowledge base loaded with {len(self.documents)} document chunks."
            self.chat.send_message(f"System: {context_summary}")
        self.ui.display_message("System", "New chat session started.", colors.INFO_BORDER)

    def get_relevant_context_for_question(self, question):
        """Get relevant context from knowledge base for a specific question"""
        return get_relevant_context(self.documents, question)

    def get_streamed_response(self, user_prompt: str):
        try:
            # Get relevant context for the question
            context = self.get_relevant_context_for_question(user_prompt)
            
            # Format the prompt with context
            if context and context != "No relevant context found.":
                formatted_prompt = f"Context information:\n{context}\n\nUser question:\n{user_prompt}"
            else:
                formatted_prompt = user_prompt
            
            response = self.chat.send_message(formatted_prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            self.ui.display_message("API Error", f"An unexpected error occurred:\n{str(e)}", colors.ERROR_BORDER)

# --- Main Application Class ---
class ChatApp:
    """The main application controller."""
    
    def __init__(self):
        self.ui = UI()
        self.llm_client = None

    def _setup(self) -> bool:
        load_dotenv(dotenv_path=ENV_FILE)
        api_key = os.getenv(API_KEY_NAME)

        if not api_key:
            self.ui.display_message("Setup Required", "API key not found.", "yellow")
            if self.ui.get_input("Configure it now? (y/n)").lower() in ['y', 'yes']:
                return self._configure_key()
            return False
        
        try:
            self.ui.console.print("[magenta]Verifying API key...[/magenta]")
            self.llm_client = LLMClient(api_key, self.ui)
            # Test API call
            genai.list_models()
            self.ui.console.print("[green]API key verified.[/green]")
            time.sleep(1.5)
            return True
        except Exception as e:
            self.ui.display_message("Error", f"Failed to initialize API client: {e}", "red")
            return False

    def _configure_key(self) -> bool:
        self.ui.clear_screen()
        self.ui.display_banner()
        self.ui.display_message("API Key Configuration", "Enter your Gemini API key (it starts with `AIza...`).", "green")
        # pwinput needs standard colorama codes for its prompt
        api_key = pwinput(prompt=f"{colorama.Fore.YELLOW}╚═> {colorama.Fore.WHITE}Paste key: {colorama.Style.RESET_ALL}", mask='*')

        if not api_key:
            self.ui.display_message("Error", "No API key entered.", "red")
            return False

        set_key(ENV_FILE, API_KEY_NAME, api_key)
        self.ui.display_message("Success", f"API key saved to {ENV_FILE}. Please restart the application.", "green")
        return True

    def _start_chat(self):
        if not self.llm_client:
            self.ui.display_message("Error", "Chat client is not initialized.", "red")
            return

        self.ui.clear_screen()
        self.ui.display_message("System", "Custom GPT is online. Type '/help' for commands.", "magenta")

        while True:
            prompt = self.ui.get_input("\nYou")
            if not prompt: continue

            if prompt.lower() == '/exit': break
            elif prompt.lower() == '/new':
                self.ui.clear_screen()
                self.llm_client.clear_history()
                continue
            elif prompt.lower() == '/help':
                self.ui.display_message("Help", "Commands:\n  /new  - Start a new conversation\n  /exit - Exit the chat", "magenta")
                continue
            
            # Pass the stream generator directly to the UI method
            stream = self.llm_client.get_streamed_response(prompt)
            self.ui.display_markdown_message("Custom GPT", stream)

    def _about_us(self):
        self.ui.display_banner()
        about_content = Text.from_markup("""
    
This is a Custom GPT Chatbot with Knowledge Base Integration.

[bold yellow]About:[/bold yellow]
   This Custom GPT is designed to work with your personal documents and knowledge base,
   providing context-aware responses based on your data.

[bold yellow]Key Features:[/bold yellow]
  • Knowledge base integration with document processing
  • Support for PDF, Word, Excel, and text files
  • Context-aware conversations
  • Beautiful terminal interface with Rich library
  • Conversation history management

[bold yellow]How to use:[/bold yellow]
  1. Place your documents in the 'knowledge' folder
  2. Run the application and start chatting
  3. Ask questions related to your documents
  4. The chatbot will use information from your documents to answer

[bold yellow]Supported File Types:[/bold yellow]
  • PDF (.pdf)
  • Word Documents (.docx)
  • Excel Spreadsheets (.xlsx, .xls)
  • Text Files (.txt)
  • Markdown Files (.md)
        """)
        self.ui.console.print(
            Panel(about_content, title="[bold cyan]About Custom GPT[/bold cyan]", border_style="green")
        )
        self.ui.get_input("\nPress Enter to return")

    def run(self):
        try:
            while True:
                self.ui.display_banner()
                self.ui.display_main_menu()
                choice = self.ui.get_input("Select an option")

                if choice == '1': 
                    if self._setup():
                        self._start_chat()
                elif choice == '2': self._configure_key()
                elif choice == '3': self._about_us()
                elif choice == '4': break
                else:
                    self.ui.display_message("Warning", "Invalid option, please try again.", "yellow")
                    time.sleep(1)
        finally:
            self.ui.console.print("[bold red]Exiting...[/bold red]")
            time.sleep(1)
            self.ui.clear_screen()

if __name__ == "__main__":
    app = ChatApp()
    app.run()