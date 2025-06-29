# MATILDA - Your Personal AI Assistant

MATILDA (My Advanced Technological Intelligence with Language Discourse Abilities) is a female version of Jarvis, designed to be your personal AI assistant. Built using the Together.ai API for natural language processing capabilities, MATILDA can help you with various tasks through intelligent conversation.

## Features

- 🧠 **Natural Language Understanding**: Powered by state-of-the-art LLM models through Together.ai
- 💬 **Conversation Management**: Maintains context throughout your conversation
- ⚙️ **Customizable Configuration**: Easily configure Matilda's behavior through environment variables
- 👤 **Personalized Experience**: Addresses you by your preferred name
- 🔍 **Contextual Responses**: Provides relevant information based on conversation history

## Installation

### Prerequisites

- Python 3.9 or higher
- A Together.ai API key (sign up at [together.ai](https://together.ai) if you don't have one)

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/MATILDA.git
   cd MATILDA
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   
   # On Windows
   .\venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   ```
   # Copy the example .env file
   copy .env.example .env
   
   # Edit the .env file with your preferred editor to add your API key
   notepad .env
   ```

## Configuration

MATILDA can be configured through environment variables in your `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `TOGETHER_API_KEY` | Your Together.ai API key | (Required) |
| `TOGETHER_MODEL` | The model to use for responses | meta-llama/Llama-3.1-405b-instruct |
| `MAX_TOKENS` | Maximum number of tokens in responses | 2048 |
| `TEMPERATURE` | Response randomness (0.0-1.0) | 0.7 |
| `VOICE_ENABLED` | Enable voice interaction (future feature) | false |
| `USERNAME` | Your preferred name | User |

## Usage

### Basic Usage

Run MATILDA from the command line:

```bash
python src/matilda.py
```

This will start an interactive session where you can chat with MATILDA.

### Example Conversation

```
Initializing Matilda...
Hello, I am Matilda. How may I assist you today, User?

You: What can you help me with?

Matilda: As your personal AI assistant, I can help you with a variety of tasks:

1. Answer questions on a wide range of topics
2. Provide information and explanations
3. Assist with problem-solving
4. Offer suggestions and recommendations
5. Engage in casual conversation

Just let me know what you need, and I'll do my best to assist you!

You: Tell me a joke

Matilda: Why don't scientists trust atoms?

Because they make up everything!

You: bye

Matilda: Goodbye! Have a nice day.
```

## Project Structure

```
MATILDA/
├── config/           # Configuration files
├── src/              # Source code
│   ├── __init__.py
│   └── matilda.py    # Main Matilda assistant class
├── tests/            # Unit tests
├── .env.example      # Example environment variables
├── .gitignore        # Git ignore file
├── README.md         # This file
└── requirements.txt  # Python dependencies
```

## Future Enhancements

- Voice interaction using text-to-speech and speech-to-text
- Integration with other APIs for enhanced capabilities
- Web interface for easier interaction
- Scheduled tasks and reminders
- Custom skills and plugins

## Troubleshooting

**Issue**: API calls are not working.  
**Solution**: Ensure your Together.ai API key is correctly set in the `.env` file.

**Issue**: Dependencies fail to install.  
**Solution**: Try installing dependencies one by one or check your internet connection.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Together.ai for providing the LLM API
- The open-source community for inspiration and tools

---

Created with ❤️ by [Your Name]

