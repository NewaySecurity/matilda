#!/usr/bin/env python
"""
Test script for verifying the connection to Together.ai API.
This script checks:
1. If environment variables are loaded correctly
2. If the API key is valid
3. If the model responds to a simple prompt
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directory to sys.path to allow importing from src
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Import required libraries
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from dotenv import load_dotenv
    import together
except ImportError as e:
    print(f"Error: Required package not found - {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

# Create console for rich output
console = Console()

def check_environment():
    """Check if environment variables are loaded correctly"""
    console.print("[bold]Testing Environment Variables...[/bold]")
    
    # Load environment variables from .env file
    dotenv_path = parent_dir / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
        console.print(f"✅ [green]Found and loaded .env file from {dotenv_path}[/green]")
    else:
        console.print(f"⚠️ [yellow]Warning: .env file not found at {dotenv_path}[/yellow]")
        console.print("[yellow]Using system environment variables instead.[/yellow]")
    
    # Check for API key
    api_key = os.environ.get("TOGETHER_API_KEY")
    if not api_key:
        console.print("❌ [red]Error: TOGETHER_API_KEY not found in environment variables[/red]")
        console.print("[yellow]Please create a .env file with your API key or set it as an environment variable.[/yellow]")
        return False
    else:
        masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "****"
        console.print(f"✅ [green]Found API key: {masked_key}[/green]")
    
    # Check for model name
    model = os.environ.get("TOGETHER_MODEL", "meta-llama/Llama-3.1-405b-instruct")
    console.print(f"✅ [green]Using model: {model}[/green]")
    
    return True

def test_api_connection():
    """Test connection to Together.ai API"""
    console.print("\n[bold]Testing API Connection...[/bold]")
    
    # Set API key
    api_key = os.environ.get("TOGETHER_API_KEY")
    together.api_key = api_key
    
    try:
        # Simple API call to check if the key is valid
        models = together.Models.list()
        console.print("✅ [green]Successfully connected to Together.ai API[/green]")
        return True
    except Exception as e:
        console.print(f"❌ [red]Error connecting to Together.ai API: {str(e)}[/red]")
        return False

def test_model_response():
    """Test if the model can generate a response"""
    console.print("\n[bold]Testing Model Response...[/bold]")
    
    model = os.environ.get("TOGETHER_MODEL", "meta-llama/Llama-3.1-405b-instruct")
    
    # Simple test prompt
    prompt = "Hello, I'm testing my connection to the Together.ai API. Please respond with a short greeting."
    
    console.print(f"[cyan]Sending test prompt to model {model}...[/cyan]")
    
    try:
        # Start timer
        start_time = time.time()
        
        # Generate response
        response = together.Complete.create(
            prompt=prompt,
            model=model,
            max_tokens=100,
            temperature=0.7
        )
        
        # End timer
        elapsed_time = time.time() - start_time
        
        # Extract response text based on response format
        # Handle different possible response formats
        response_text = ""
        if isinstance(response, dict):
            if "output" in response:
                # New API format directly provides output
                response_text = response["output"]["text"].strip()
            elif "choices" in response:
                # Old API format with choices array
                response_text = response["choices"][0]["text"].strip()
            elif "generated_text" in response:
                # Another possible format
                response_text = response["generated_text"].strip()
            else:
                # Debug response structure
                console.print(f"[yellow]Response structure: {list(response.keys())}[/yellow]")
                response_text = str(response)
        else:
            # Handle object-style response
            if hasattr(response, "choices") and response.choices:
                response_text = response.choices[0].text.strip()
            elif hasattr(response, "output") and response.output:
                response_text = response.output.text.strip()
            else:
                response_text = str(response)
        
        console.print(f"✅ [green]Received response in {elapsed_time:.2f} seconds[/green]")
        
        # Display response in a panel
        response_panel = Panel(
            Text(response_text, style="green"),
            title="Model Response",
            border_style="green"
        )
        console.print(response_panel)
        
        return True
    except Exception as e:
        error_msg = str(e)
        console.print(f"❌ [red]Error getting model response: {error_msg}[/red]")
        
        # Provide more helpful guidance for specific errors
        if "model_not_available" in error_msg or "model not found" in error_msg.lower():
            console.print("\n[yellow]The specified model is not available through Together.ai.[/yellow]")
            console.print("[yellow]Please try the following:[/yellow]")
            console.print("1. Check available models at: [link]https://api.together.ai/models[/link]")
            console.print("2. Update your .env file with an available model name")
            console.print("3. Example models that are commonly available:")
            console.print("   - togethercomputer/llama-2-70b-chat")
            console.print("   - mistralai/Mixtral-8x7B-Instruct-v0.1")
            console.print("   - meta-llama/Llama-2-70b-chat-hf")
        elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
            console.print("\n[yellow]There appears to be an issue with your API key.[/yellow]")
            console.print("[yellow]Please verify that your API key is correct in the .env file.[/yellow]")
        
        return False

def main():
    """Run all tests"""
    console.print(Panel.fit(
        "[bold cyan]MATILDA - Together.ai Connection Test[/bold cyan]",
        border_style="cyan"
    ))
    
    # Run tests
    env_check = check_environment()
    if not env_check:
        console.print("\n[bold red]Environment check failed. Please fix the issues above and try again.[/bold red]")
        return
    
    api_check = test_api_connection()
    if not api_check:
        console.print("\n[bold red]API connection test failed. Please check your API key and internet connection.[/bold red]")
        return
    
    model_check = test_model_response()
    if not model_check:
        console.print("\n[bold red]Model response test failed. Please check the error message above.[/bold red]")
        return
    
    # All tests passed
    console.print("\n[bold green]✨ All tests passed! Your Matilda setup is working correctly.[/bold green]")
    console.print("[green]You can now use Matilda by running: python src/matilda.py[/green]")

if __name__ == "__main__":
    main()

