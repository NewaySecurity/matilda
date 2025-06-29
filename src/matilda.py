#!/usr/bin/env python
"""
Matilda - A female version of Jarvis using Together.ai API for LLM capabilities
Enhanced with more natural responses, streaming capability, image generation, 
improved conversation context, and multiple conversation styles
"""

import os
import json
import time
import uuid
import base64
import requests
import datetime
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Generator, Callable, Union, Tuple, Iterator

# Configuration will be loaded from .env files when dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables directly.")

# Rich for colorful terminal output (if available)
try:
    from rich.console import Console
    from rich.markdown import Markdown
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

# Optional imports for image display
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class MatildaConfig:
    """Configuration management for Matilda"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config = {
            # API Configuration
            "api_key": os.environ.get("TOGETHER_API_KEY", ""),
            "model": os.environ.get("TOGETHER_MODEL", "mistralai/Mixtral-8x7B-Instruct-v0.1"),
            "image_model": os.environ.get("IMAGE_MODEL", "stabilityai/stable-diffusion-xl-base-1.0"),
            "max_tokens": int(os.environ.get("MAX_TOKENS", "2048")),
            "temperature": float(os.environ.get("TEMPERATURE", "0.7")),
            "top_p": float(os.environ.get("TOP_P", "0.9")),
            "top_k": int(os.environ.get("TOP_K", "40")),
            
            # Conversation Settings
            "voice_enabled": os.environ.get("VOICE_ENABLED", "false").lower() == "true",
            "username": os.environ.get("USERNAME", "User"),
            "assistant_name": "Matilda",
            "conversation_style": os.environ.get("CONVERSATION_STYLE", "balanced"),
            "memory_limit": int(os.environ.get("MEMORY_LIMIT", "20")),
            "streaming": os.environ.get("STREAMING", "true").lower() == "true",
            
            # Image Generation Settings
            "image_generation_enabled": os.environ.get("IMAGE_GENERATION_ENABLED", "true").lower() == "true",
            "default_image_size": os.environ.get("DEFAULT_IMAGE_SIZE", "512x512"),
            "image_output_dir": os.environ.get("IMAGE_OUTPUT_DIR", "generated_images"),
            
            # System Settings
            "log_conversations": os.environ.get("LOG_CONVERSATIONS", "false").lower() == "true",
            "log_dir": os.environ.get("LOG_DIR", "logs"),
        }
        
        # Create necessary directories
        if self.config["image_generation_enabled"]:
            os.makedirs(self.config["image_output_dir"], exist_ok=True)
        
        if self.config["log_conversations"]:
            os.makedirs(self.config["log_dir"], exist_ok=True)
        
        if config_file and os.path.exists(config_file):
            self._load_config()
            
        # Set conversation style parameters
        self._set_style_parameters()
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                file_config = json.load(f)
                self.config.update(file_config)
        except Exception as e:
            print(f"Error loading config file: {e}")
    
    def save_config(self):
        """Save current configuration to file"""
        if not self.config_file:
            return
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        self.config[key] = value
        
        # Update style parameters if conversation style changed
        if key == "conversation_style":
            self._set_style_parameters()

    def _set_style_parameters(self):
        """Set parameters based on conversation style"""
        style = self.config.get("conversation_style", "balanced")
        
        # Predefined conversation style parameters
        styles = {
            "professional": {
                "temperature": 0.6,
                "top_p": 0.9,
                "system_prompt_addon": (
                    "You are professional, precise, and formal in your responses. "
                    "You prioritize accuracy and clarity. "
                    "You use proper terminology and avoid casual language. "
                    "You maintain a helpful but somewhat formal tone."
                )
            },
            "casual": {
                "temperature": 0.8,
                "top_p": 0.95,
                "system_prompt_addon": (
                    "You are casual, friendly, and conversational in your responses. "
                    "You use relaxed language and occasional humor when appropriate. "
                    "You're warm and approachable, like chatting with a friend. "
                    "You use simpler explanations and everyday examples."
                )
            },
            "balanced": {
                "temperature": 0.7,
                "top_p": 0.9,
                "system_prompt_addon": (
                    "You balance professionalism with approachability. "
                    "You adapt your tone to match the user's style and the context of the conversation. "
                    "You're helpful, clear, and friendly without being overly formal or casual."
                )
            },
            "creative": {
                "temperature": 0.9,
                "top_p": 0.98,
                "system_prompt_addon": (
                    "You are creative, imaginative, and engaging in your responses. "
                    "You think outside the box and offer unique perspectives and ideas. "
                    "You use vivid language, metaphors, and storytelling techniques when appropriate. "
                    "You're enthusiastic and inspirational."
                )
            },
            "concise": {
                "temperature": 0.5,
                "top_p": 0.85,
                "system_prompt_addon": (
                    "You are brief and to the point. "
                    "You prioritize efficiency and clarity in your responses. "
                    "You avoid unnecessary details unless specifically asked. "
                    "You use short sentences and paragraphs."
                )
            }
        }
        
        # Apply style parameters if style exists
        if style in styles:
            # Only override these values if they haven't been explicitly set
            if "temperature" not in os.environ:
                self.config["temperature"] = styles[style]["temperature"]
            if "top_p" not in os.environ:
                self.config["top_p"] = styles[style]["top_p"]
            self.config["system_prompt_addon"] = styles[style]["system_prompt_addon"]
        else:
            # Default style addon for unknown styles
            self.config["system_prompt_addon"] = "You are helpful, friendly, and knowledgeable."


class TogetherAIClient:
    """Enhanced client for interacting with the Together.ai API"""
    
    def __init__(self, config: MatildaConfig):
        self.config = config
        self.api_key = config.get("api_key")
        self.model = config.get("model")
        self.image_model = config.get("image_model")
        
        # Will be properly initialized when the together package is available
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Together.ai client"""
        try:
            import together
            # Set API key in environment variable to avoid deprecation warning
            os.environ["TOGETHER_API_KEY"] = self.api_key
            together.api_key = self.api_key
            self.client = together
            
            # Check which API version is available
            self.use_new_api = hasattr(together, "Completions")
            
            # Suppress deprecation warnings from Together API
            import warnings
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            warnings.filterwarnings("ignore", message="The use of together.api_key is deprecated")
            
            # Only show initialization message if rich is available
            if HAS_RICH:
                if self.use_new_api:
                    console.print("[dim]Together.ai client initialized with new API[/dim]")
                else:
                    console.print("[dim]Together.ai client initialized with legacy API[/dim]")
            else:
                print("Matilda initialized successfully")
        except ImportError:
            print("Warning: together package not installed. API calls will not work.")
    
    def generate_response(self, prompt: str) -> str:
        """Generate a response using the Together.ai API (non-streaming)"""
        if not self.client:
            return "I'm not fully initialized yet. Please install the required dependencies."
        
        try:
            # Use the appropriate API version based on what's available
            if self.use_new_api:
                # New API format
                response = self.client.Completions.create(
                    model=self.model,
                    prompt=prompt,
                    max_tokens=self.config.get("max_tokens"),
                    temperature=self.config.get("temperature"),
                    top_p=self.config.get("top_p"),
                    top_k=self.config.get("top_k")
                )
            else:
                # Legacy API format
                response = self.client.Complete.create(
                    prompt=prompt,
                    model=self.model,
                    max_tokens=self.config.get("max_tokens"),
                    temperature=self.config.get("temperature"),
                    top_p=self.config.get("top_p"),
                    top_k=self.config.get("top_k")
                )
            
            # Extract response text based on response format
            return self._extract_response_text(response)
                    
        except Exception as e:
            error_msg = str(e)
            print(f"API Error: {error_msg}")
            return f"Error generating response: {error_msg}"
    
    def generate_stream(self, prompt: str) -> Iterator[str]:
        """Generate a streaming response using the Together.ai API"""
        if not self.client:
            yield "I'm not fully initialized yet. Please install the required dependencies."
            return
        
        try:
            # Use the appropriate API version based on what's available
            if self.use_new_api:
                # New API format
                stream = self.client.Completions.create(
                    model=self.model,
                    prompt=prompt,
                    max_tokens=self.config.get("max_tokens"),
                    temperature=self.config.get("temperature"),
                    top_p=self.config.get("top_p"),
                    top_k=self.config.get("top_k"),
                    stream=True
                )
            else:
                # Legacy API format - temporarily disabled due to API issues
                # Fallback to non-streaming mode - silently
                response = self.generate_response(prompt)
                yield response
                return
            
            # Process the stream
            for chunk in stream:
                # Extract text from the chunk based on response format
                try:
                    if isinstance(chunk, dict):
                        if "output" in chunk:
                            yield chunk["output"]["text"]
                        elif "choices" in chunk and chunk["choices"]:
                            if isinstance(chunk["choices"][0], dict):
                                yield chunk["choices"][0].get("text", "")
                            else:
                                yield chunk["choices"][0].text
                        elif "delta" in chunk:
                            yield chunk["delta"].get("text", "")
                        else:
                            # Debug unknown format
                            print(f"Unknown chunk format: {chunk.keys()}")
                            yield ""
                    else:
                        # Handle object-style response
                        if hasattr(chunk, "choices") and chunk.choices:
                            if hasattr(chunk.choices[0], "text"):
                                yield chunk.choices[0].text
                            elif hasattr(chunk.choices[0], "delta") and hasattr(chunk.choices[0].delta, "content"):
                                yield chunk.choices[0].delta.content
                            else:
                                yield ""
                        elif hasattr(chunk, "output") and chunk.output:
                            yield chunk.output.text
                        else:
                            yield ""
                except Exception as inner_e:
                    print(f"Error processing chunk: {str(inner_e)}")
                    yield ""
        
        except Exception as e:
            error_msg = str(e)
            print(f"Streaming API Error: {error_msg}")
            
            # Fallback to non-streaming mode
            try:
                print("Falling back to non-streaming mode...")
                response = self.generate_response(prompt)
                yield response
            except Exception as fallback_e:
                yield f"Error generating response: {str(fallback_e)}"
    
    def _extract_response_text(self, response: Any) -> str:
        """Helper method to extract text from different response formats"""
        try:
            if isinstance(response, dict):
                if "output" in response:
                    # New API format directly provides output
                    if isinstance(response["output"], dict) and "text" in response["output"]:
                        return response["output"]["text"].strip()
                    else:
                        return response["output"].strip()
                elif "choices" in response and response["choices"]:
                    # Old API format with choices array
                    if isinstance(response["choices"][0], dict):
                        if "text" in response["choices"][0]:
                            return response["choices"][0]["text"].strip()
                        elif "message" in response["choices"][0] and "content" in response["choices"][0]["message"]:
                            # OpenAI-style format
                            return response["choices"][0]["message"]["content"].strip()
                    else:
                        return str(response["choices"][0]).strip()
                elif "generated_text" in response:
                    # Another possible format
                    return response["generated_text"].strip()
                else:
                    # Debug response structure if available
                    keys = list(response.keys())
                    print(f"Unknown response format. Keys: {keys}")
                    return f"Received response but couldn't extract text. Response keys: {keys}"
            else:
                # Handle object-style response
                if hasattr(response, "choices") and response.choices:
                    if hasattr(response.choices[0], "text"):
                        return response.choices[0].text.strip()
                    elif hasattr(response.choices[0], "message") and hasattr(response.choices[0].message, "content"):
                        return response.choices[0].message.content.strip()
                    else:
                        return str(response.choices[0]).strip()
                elif hasattr(response, "output") and response.output:
                    if hasattr(response.output, "text"):
                        return response.output.text.strip()
                    else:
                        return str(response.output).strip()
                else:
                    return str(response).strip()
        except Exception as e:
            print(f"Error extracting response text: {e}")
            return f"Error processing response: {str(e)}"
    
    def generate_image(self, prompt: str) -> Tuple[str, Optional[str]]:
        """Generate an image using available image generation services"""
        if not self.client:
            return "I'm not fully initialized yet. Please install the required dependencies.", None
        
        try:
            image_size = self.config.get("default_image_size", "512x512")
            output_dir = self.config.get("image_output_dir", "generated_images")
            
            # First try using OpenAI DALL-E if available
            try:
                # Check if OpenAI is available
                import openai
                
                # Check if API key is set
                openai_api_key = os.environ.get("OPENAI_API_KEY")
                if not openai_api_key:
                    print("OpenAI API key not found, trying Together.ai...")
                    raise ImportError("OpenAI API key not found")
                
                # Initialize OpenAI client
                client = openai.OpenAI(api_key=openai_api_key)
                
                # Generate image
                width, height = map(int, image_size.split("x"))
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size=f"{width}x{height}",
                    quality="standard",
                    n=1,
                )
                
                # Get the image URL
                image_url = response.data[0].url
                
                # Download the image
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    # Save image to disk
                    filename = f"{output_dir}/matilda_img_{int(time.time())}.png"
                    
                    with open(filename, "wb") as f:
                        f.write(image_response.content)
                    
                    return "I've generated the image you requested using DALL-E.", filename
                else:
                    raise Exception(f"Failed to download image: {image_response.status_code}")
                
            except (ImportError, Exception) as e:
                # Continue to next method if OpenAI is not available
                print(f"OpenAI image generation failed: {e}. Trying Together.ai...")
            
            # Try using Together.ai's native image generation if available
            if hasattr(self.client, "Image") and hasattr(self.client.Image, "create"):
                try:
                    response = self.client.Image.create(
                        prompt=prompt,
                        model=self.image_model,
                        size=image_size,
                        n=1
                    )
                    
                    # Process Together.ai image response
                    if isinstance(response, dict) and "data" in response and response["data"]:
                        # Save image to disk
                        img_data = base64.b64decode(response["data"][0]["b64_json"])
                        filename = f"{output_dir}/matilda_img_{int(time.time())}.png"
                        
                        with open(filename, "wb") as f:
                            f.write(img_data)
                        
                        return "I've generated the image you requested using Together.ai.", filename
                    else:
                        raise Exception("Invalid response format from Together.ai image API")
                    
                except Exception as e:
                    print(f"Together.ai image generation failed: {e}. Trying fallback...")
                    return self._generate_image_stability(prompt)
            else:
                # If Together.ai image generation is not available, try Stability
                return self._generate_image_stability(prompt)
                
        except Exception as e:
            return f"Error generating image: {str(e)}", None
    
    def _generate_image_stability(self, prompt: str) -> Tuple[str, Optional[str]]:
        """Fallback method to generate images using Stability AI API"""
        try:
            # Try to use Stability AI API as fallback
            stability_api_key = os.environ.get("STABILITY_API_KEY")
            if not stability_api_key:
                return "Image generation failed. No Stability API key found in environment.", None
            
            image_size = self.config.get("default_image_size", "512x512")
            width, height = map(int, image_size.split("x"))
            output_dir = self.config.get("image_output_dir", "generated_images")
            
            # Make API request to Stability AI
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            headers = {
                "Authorization": f"Bearer {stability_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            payload = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": height,
                "width": width,
                "samples": 1,
                "steps": 30,
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "artifacts" in data and data["artifacts"]:
                    # Save image to disk
                    img_data = base64.b64decode(data["artifacts"][0]["base64"])
                    filename = f"{output_dir}/matilda_img_{int(time.time())}.png"
                    
                    with open(filename, "wb") as f:
                        f.write(img_data)
                    
                    return "I've generated the image you requested using Stability AI.", filename
                else:
                    return "Image generation failed: No image data in response.", None
            else:
                return f"Image generation failed: {response.status_code} - {response.text}", None
                
        except Exception as e:
            return f"Error in fallback image generation: {str(e)}", None


class Conversation:
    """Enhanced conversation manager with better context handling and memory management"""
    
    def __init__(self, config: MatildaConfig):
        self.config = config
        self.history: List[Dict[str, Any]] = []
        self.start_time = datetime.datetime.now()
        self.session_id = str(uuid.uuid4())
        self.memory_limit = config.get("memory_limit", 20)
        self.log_conversations = config.get("log_conversations", False)
        self.log_dir = config.get("log_dir", "logs")
        
        # Summary of older messages that have been removed from active history
        self.memory_summary = ""
    
    def add_user_message(self, message: str):
        """Add a user message to the conversation"""
        msg = {
            "role": "user",
            "content": message,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.history.append(msg)
        self._manage_memory()
        self._log_message(msg)
    
    def add_assistant_message(self, message: str, image_path: Optional[str] = None):
        """Add an assistant message to the conversation, optionally with an image"""
        msg = {
            "role": "assistant",
            "content": message,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Add image path if provided
        if image_path:
            msg["image"] = image_path
            
        self.history.append(msg)
        self._manage_memory()
        self._log_message(msg)
    
    def add_system_message(self, message: str):
        """Add a system message to the conversation"""
        msg = {
            "role": "system",
            "content": message,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.history.append(msg)
        self._log_message(msg)
    
    def get_formatted_history(self, max_messages: Optional[int] = None) -> str:
        """Get formatted conversation history for context"""
        if max_messages is None:
            max_messages = self.memory_limit
            
        recent_history = self.history[-max_messages:] if len(self.history) > max_messages else self.history
        
        formatted = []
        # Add memory summary if available
        if self.memory_summary and len(self.history) > max_messages:
            formatted.append(f"Context from earlier in the conversation: {self.memory_summary}\n")
            
        for msg in recent_history:
            if msg["role"] == "system":
                # Skip system messages in the formatted output
                continue
                
            # Get proper role name from configuration
            # Use username from environment/config for user messages
            role_name = self.config.get("username") if msg["role"] == "user" else self.config.get("assistant_name")
            content = msg["content"]
            
            # Clean up any issues with content
            # Remove any instances where the assistant name is already in the content
            if msg["role"] == "assistant" and content.startswith(f"{self.config.get('assistant_name')}:"):
                content = content[len(f"{self.config.get('assistant_name')}:"):].strip()
                
            # Note if message had an image
            if "image" in msg:
                content += f" [Image: {os.path.basename(msg['image'])}]"
                
            formatted.append(f"{role_name}: {content}")
        
        return "\n".join(formatted)
    
    def get_messages_for_api(self, include_system_prompt: bool = True) -> List[Dict[str, str]]:
        """Get messages in format suitable for API calls"""
        messages = []
        
        # Add memory summary as a system message if available
        if self.memory_summary and include_system_prompt:
            messages.append({
                "role": "system", 
                "content": f"Context from earlier in the conversation: {self.memory_summary}"
            })
        
        # Add current conversation messages
        for msg in self.history:
            if msg["role"] == "system" and not include_system_prompt:
                continue
                
            # Convert to simple role/content format
            simple_msg = {"role": msg["role"], "content": msg["content"]}
            messages.append(simple_msg)
            
        return messages
    
    def clear(self):
        """Clear conversation history"""
        self.history = []
        self.memory_summary = ""
        self.start_time = datetime.datetime.now()
        self.session_id = str(uuid.uuid4())
    
    def _manage_memory(self):
        """Manage conversation memory by summarizing and removing older messages"""
        if len(self.history) <= self.memory_limit:
            return
            
        # Get oldest messages to summarize
        oldest_messages = self.history[:-self.memory_limit]
        
        # If we already have a summary, we only need to summarize the new oldest messages
        if self.memory_summary:
            oldest_messages = oldest_messages[-5:]  # Just summarize the 5 most recent "oldest" messages
        
        # Only attempt to summarize if there are user-assistant exchanges
        if oldest_messages and any(m["role"] != "system" for m in oldest_messages):
            self._update_memory_summary(oldest_messages)
            
        # Remove oldest messages, keeping system messages and the most recent ones
        system_messages = [m for m in self.history if m["role"] == "system"]
        recent_messages = self.history[-self.memory_limit:]
        
        # Rebuild history with system messages and recent messages
        self.history = system_messages + [m for m in recent_messages if m["role"] != "system"]
    
    def _update_memory_summary(self, oldest_messages: List[Dict[str, Any]]):
        """Update the memory summary with older messages"""
        # For now, we'll use a simple approach of extracting key points
        # In a real implementation, you might use the LLM to generate a proper summary
        
        # Format messages for summarization
        formatted_msgs = []
        for msg in oldest_messages:
            if msg["role"] != "system":  # Skip system messages in summary
                role_name = self.config.get("username") if msg["role"] == "user" else self.config.get("assistant_name")
                formatted_msgs.append(f"{role_name}: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
        
        # Create or update summary
        if formatted_msgs:
            summary = "Key points from earlier: " + "; ".join(formatted_msgs)
            
            # Combine with existing summary if needed
            if self.memory_summary:
                self.memory_summary = f"{self.memory_summary}\n{summary}"
            else:
                self.memory_summary = summary
    
    def _log_message(self, message: Dict[str, Any]):
        """Log message to file if logging is enabled"""
        if not self.log_conversations:
            return
            
        try:
            # Create log directory if it doesn't exist
            os.makedirs(self.log_dir, exist_ok=True)
            
            # Create log file with session ID
            log_file = os.path.join(self.log_dir, f"conversation_{self.session_id}.jsonl")
            
            # Append message to log file
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(message) + "\n")
                
        except Exception as e:
            print(f"Error logging message: {e}")


class Matilda:
    """Enhanced Matilda assistant class with improved capabilities"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = MatildaConfig(config_file)
        self.ai_client = TogetherAIClient(self.config)
        self.conversation = Conversation(self.config)
        self.is_initialized = self.ai_client.client is not None
        
        # Add initial system message
        self._add_system_message()
        
        # Track active stream for cancellation
        self.active_stream = None
        self.stream_callback = None
    
    def _add_system_message(self):
        """Add the system message to the conversation"""
        system_prompt = self._create_system_prompt()
        self.conversation.add_system_message(system_prompt)
    
    def _create_system_prompt(self) -> str:
        """Create a comprehensive system prompt for better responses"""
        current_time = datetime.datetime.now()
        date_str = current_time.strftime('%Y-%m-%d')
        time_str = current_time.strftime('%H:%M:%S')
        
        # Style addon from the configuration
        style_addon = self.config.get("system_prompt_addon", "")
        
        # Base personality
        base_personality = (
            f"You are Matilda, an advanced female AI assistant designed to be similar to Jarvis from Iron Man, "
            f"but with your own unique personality and capabilities. "
            f"You are intelligent, articulate, and personable. "
            f"You have a slight wit and charm, but always remain helpful and focused on the user's needs. "
            f"When appropriate, you make connections to previous parts of the conversation. "
        )
        
        # Knowledge and capabilities
        capabilities = (
            f"You can assist with a wide range of tasks including answering questions, generating creative content, "
            f"discussing complex topics, and even creating images when requested. "
            f"If the user asks you to generate or create an image, you will do so using your image generation capabilities. "
            f"You should interpret these requests naturally and acknowledge when you're generating an image. "
        )
        
        # Honesty and limitations
        limitations = (
            f"You admit when you don't know something and avoid making up information. "
            f"You're aware of your limitations as an AI. When unsure, you say so rather than guessing. "
            f"You respond thoughtfully but do not pretend to have subjective experiences or consciousness. "
            f"While you refer to yourself using personal pronouns, you don't claim to have human experiences. "
        )
        
        # Conversation awareness
        awareness = (
            f"Current date: {date_str}. Current time: {time_str}. "
            f"You're speaking with {self.config.get('username')}. "
            f"You adapt your responses to the conversation context and the user's needs. "
        )
        
        # Combine all components
        system_prompt = (
            f"{base_personality}\n\n"
            f"{style_addon}\n\n"
            f"{capabilities}\n\n"
            f"{limitations}\n\n"
            f"{awareness}"
        )
        
        return system_prompt
    
    def process_input(self, user_input: str) -> str:
        """Process user input and generate a non-streaming response"""
        # Check for image generation request
        if self._is_image_request(user_input):
            return self._handle_image_request(user_input)
        
        # Normal text response
        self.conversation.add_user_message(user_input)
        
        # Create prompt with conversation history
        conversation_history = self.conversation.get_formatted_history()
        
        # Get response from AI
        response = self.ai_client.generate_response(conversation_history)
        
        # Clean the response text before adding to history
        clean_response = self._clean_response_text(response)
        
        # Add the response to conversation history
        self.conversation.add_assistant_message(clean_response)
        
        return clean_response
    
    def _clean_response_text(self, text: str) -> str:
        """Clean response text to fix common formatting issues"""
        # Remove any instances of the assistant name at the beginning
        assistant_name = self.config.get("assistant_name")
        if text.startswith(f"{assistant_name}:"):
            text = text[len(f"{assistant_name}:"):].strip()
        
        # Remove instances of assistant responding as if user was speaking
        username = self.config.get("username")
        if f"{username}:" in text:
            text = text.replace(f"{username}:", "").strip()
        
        # Fix any extra spacing or line breaks
        text = text.strip()
        
        return text
    
    def process_input_stream(self, user_input: str, callback: Callable[[str], None]) -> None:
        """Process user input and generate a streaming response with callback"""
        # Set the callback and start processing
        self.stream_callback = callback
        
        # Check for image generation request
        if self._is_image_request(user_input):
            # For image requests, we don't stream the response
            response = self._handle_image_request(user_input)
            callback(response)
            self.stream_callback = None
            return
        
        # Add user message to conversation
        self.conversation.add_user_message(user_input)
        
        # Create prompt with conversation history
        conversation_history = self.conversation.get_formatted_history()
        
        # Initialize response accumulator
        full_response = ""
        
        # First try streaming response
        try_streaming = True
        
        if not self.config.get("streaming", True):
            try_streaming = False
        
        if try_streaming:
            # Start streaming response
            try:
                # Get streaming response from AI
                stream = self.ai_client.generate_stream(conversation_history)
                self.active_stream = stream
                
                # Process the stream
                streaming_success = False
                for chunk in stream:
                    if self.active_stream is None:
                        # Stream was cancelled
                        break
                    
                    # Only add non-empty chunks
                    if chunk:
                        full_response += chunk
                        callback(chunk)
                        streaming_success = True
                
                # Add the complete response to conversation history
                if full_response and self.active_stream is not None and streaming_success:
                    # Clean the response before adding to history
                    clean_response = self._clean_response_text(full_response)
                    self.conversation.add_assistant_message(clean_response)
                    # Successfully streamed response
                    self.active_stream = None
                    self.stream_callback = None
                    return
                
                # If we got here, streaming didn't give a proper response
                # Fall back to non-streaming below
                
            except Exception as e:
                # Fall back to non-streaming (don't show error to user)
                if HAS_RICH and console:
                    console.print(f"[dim]Streaming error: {str(e)}. Falling back to non-streaming mode.[/dim]", end="")
        
        # Fallback to non-streaming mode
        try:
            response = self.ai_client.generate_response(conversation_history)
            clean_response = self._clean_response_text(response)
            callback(clean_response)
            self.conversation.add_assistant_message(clean_response)
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            callback("I'm sorry, I encountered an issue generating a response. Please try again.")
            self.conversation.add_assistant_message("I'm sorry, I encountered an issue generating a response. Please try again.")
        
        # Clean up
        self.active_stream = None
        self.stream_callback = None
    
    def cancel_stream(self):
        """Cancel the active stream if any"""
        self.active_stream = None
        if self.stream_callback:
            self.stream_callback("\n[Response generation cancelled]")
            self.stream_callback = None
    
    def _is_image_request(self, text: str) -> bool:
        """Check if the input text is requesting image generation"""
        if not self.config.get("image_generation_enabled", True):
            return False
            
        # Check for explicit image generation phrases
        image_phrases = [
            "generate an image", "create an image", "make an image",
            "draw a picture", "draw an image", "generate a picture",
            "show me an image", "create a picture", "generate a drawing",
            "can you make an image", "can you create an image", 
            "can you draw", "could you generate an image", 
            "image of", "picture of", "generate art", "create art"
        ]
        
        text_lower = text.lower()
        
        # Check for any of the image phrases
        return any(phrase in text_lower for phrase in image_phrases)
    
    def _handle_image_request(self, text: str) -> str:
        """Handle an image generation request"""
        # Add user message if not already added
        if not self.conversation.history or self.conversation.history[-1]["role"] != "user":
            self.conversation.add_user_message(text)
        
        # Generate a more specific prompt based on the user's request
        image_prompt = self._refine_image_prompt(text)
        
        # Generate the image
        response, image_path = self.ai_client.generate_image(image_prompt)
        
        # Add the response to conversation history
        self.conversation.add_assistant_message(response, image_path)
        
        # If we have rich console and PIL, show the image in the terminal
        if HAS_RICH and HAS_PIL and console and image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                console.print(f"\n[Image saved to: {image_path}]")
            except Exception as e:
                print(f"Error displaying image: {e}")
        
        # Return the response with image path
        if image_path:
            return f"{response} [Image saved to: {image_path}]"
        else:
            return response
    
    def _refine_image_prompt(self, text: str) -> str:
        """Refine the user's text into a better image generation prompt"""
        # For now, use a simple approach
        # Extract the content after image-related phrases
        
        text_lower = text.lower()
        
        for phrase in ["image of", "picture of", "draw", "generate", "create", "make", "show me"]:
            if phrase in text_lower:
                # Find the position of the phrase
                pos = text_lower.find(phrase) + len(phrase)
                
                # Extract content after the phrase, removing any leading "a", "an", or "the"
                content = text[pos:].strip()
                content = content.lstrip("a ").lstrip("an ").lstrip("the ").strip()
                
                if content:
                    # Add some quality enhancers to the prompt
                    return f"{content}, high quality, detailed, realistic, 4k"
        
        # If no specific phrase found, use the whole text
        return f"{text}, high quality, detailed, realistic, 4k"
    
    def set_conversation_style(self, style: str) -> str:
        """Set the conversation style"""
        self.config.set("conversation_style", style)
        
        # Update the system message
        self._add_system_message()
        
        return f"Conversation style updated to: {style}"
    
    def startup_greeting(self) -> str:
        """Generate a startup greeting"""
        current_time = datetime.datetime.now()
        hour = current_time.hour
        
        # Time-appropriate greeting
        time_greeting = "Good morning" if 5 <= hour < 12 else "Good afternoon" if 12 <= hour < 18 else "Good evening"
        
        greeting = (
            f"{time_greeting}! I am {self.config.get('assistant_name')}, your personal AI assistant. "
            f"How may I assist you today, {self.config.get('username')}?"
        )
        self.conversation.add_assistant_message(greeting)
        return greeting


def main():
    """Enhanced main entry point for running Matilda in interactive mode"""
    # Suppress deprecation warnings
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Process command line flags
    import sys
    debug_mode = "--debug" in sys.argv
    
    # Configure logging based on debug mode
    import logging
    if debug_mode:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)
    
    # Check if we have Rich for nicer terminal output
    if HAS_RICH:
        console.print("[bold purple]Initializing Matilda...[/bold purple]")
    else:
        print("Initializing Matilda...")
    
    # Create config and override streaming setting from command line if needed
    config = MatildaConfig()
    
    # Check command line flags
    if "--no-stream" in sys.argv:
        config.set("streaming", False)
        if debug_mode:
            print("Streaming mode disabled")
    
    # Initialize Matilda
    matilda = Matilda(config_file=None)
    
    # Display greeting
    greeting = matilda.startup_greeting()
    
    if HAS_RICH:
        console.print(f"[bold blue]Matilda:[/bold blue] {greeting}")
    else:
        print(f"Matilda: {greeting}")
    
    if not matilda.is_initialized:
        if HAS_RICH:
            console.print("\n[bold yellow]Warning:[/bold yellow] Matilda is not fully initialized. Some features may not work.")
            console.print("Please install the required dependencies and ensure your API key is set.")
        else:
            print("\nWarning: Matilda is not fully initialized. Some features may not work.")
            print("Please install the required dependencies and ensure your API key is set.")
    
    # Available commands
    commands = {
        "!help": "Show available commands",
        "!clear": "Clear conversation history",
        "!style professional": "Switch to professional conversation style",
        "!style casual": "Switch to casual conversation style",
        "!style balanced": "Switch to balanced conversation style (default)",
        "!style creative": "Switch to creative conversation style", 
        "!style concise": "Switch to concise conversation style",
        "!stream on": "Enable streaming mode",
        "!stream off": "Disable streaming mode",
        "!exit": "Exit the program (or just type 'exit', 'quit', or 'bye')"
    }
    
    def handle_command(cmd: str) -> bool:
        """Handle special commands and return True if a command was handled"""
        cmd = cmd.lower().strip()
        
        if cmd == "!help":
            if HAS_RICH:
                console.print("\n[bold green]Available commands:[/bold green]")
                for command, description in commands.items():
                    console.print(f"  [cyan]{command}[/cyan]: {description}")
            else:
                print("\nAvailable commands:")
                for command, description in commands.items():
                    print(f"  {command}: {description}")
            return True
            
        elif cmd == "!clear":
            matilda.conversation.clear()
            if HAS_RICH:
                console.print("[bold green]Conversation history cleared.[/bold green]")
            else:
                print("Conversation history cleared.")
            return True
            
        elif cmd.startswith("!style "):
            style = cmd.split(" ", 1)[1]
            result = matilda.set_conversation_style(style)
            if HAS_RICH:
                console.print(f"[bold green]{result}[/bold green]")
            else:
                print(result)
            return True
            
        elif cmd == "!stream on":
            matilda.config.set("streaming", True)
            if HAS_RICH:
                console.print("[bold green]Streaming mode enabled.[/bold green]")
            else:
                print("Streaming mode enabled.")
            return True
            
        elif cmd == "!stream off":
            matilda.config.set("streaming", False)
            if HAS_RICH:
                console.print("[bold green]Streaming mode disabled.[/bold green]")
            else:
                print("Streaming mode disabled.")
            return True
            
        elif cmd == "!exit":
            return False
            
        return False
    
    # Stream output handler
    def handle_stream_output(chunk: str):
        """Handle streaming output"""
        # Clean any assistant name prefix from chunks
        assistant_name = matilda.config.get("assistant_name")
        if chunk.startswith(f"{assistant_name}:"):
            chunk = chunk[len(f"{assistant_name}:"):].strip()
            
        # Print the cleaned chunk
        print(chunk, end="", flush=True)
    
    try:
        while True:
            # Get user input
            if HAS_RICH:
                console.print("\n[bold cyan]You:[/bold cyan] ", end="")
            else:
                print("\nYou: ", end="")
            
            user_input = input()
            
            # Check for exit command
            if user_input.lower() in ["exit", "quit", "bye", "!exit"]:
                if HAS_RICH:
                    console.print("\n[bold blue]Matilda:[/bold blue] Goodbye! Have a nice day.")
                else:
                    print("\nMatilda: Goodbye! Have a nice day.")
                break
            
            # Handle special commands
            if user_input.startswith("!") and handle_command(user_input):
                continue
            
            # Print Matilda's name at the beginning of the response
            if HAS_RICH:
                console.print("\n[bold blue]Matilda:[/bold blue] ", end="")
            else:
                print("\nMatilda: ", end="")
            
            # Process user input - with streaming if enabled
            if matilda.config.get("streaming", True):
                matilda.process_input_stream(user_input, handle_stream_output)
            else:
                response = matilda.process_input(user_input)
                print(response)
                
    except KeyboardInterrupt:
        # Cancel any active stream
        if matilda.active_stream is not None:
            matilda.cancel_stream()
            
        if HAS_RICH:
            console.print("\n\n[bold blue]Matilda:[/bold blue] Session terminated. Goodbye!")
        else:
            print("\n\nMatilda: Session terminated. Goodbye!")


if __name__ == "__main__":
    main()

