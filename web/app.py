#!/usr/bin/env python
"""
Web application for Matilda using Flask
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session

# Add the parent directory to sys.path to allow importing from src
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Import Matilda from src
from src.matilda import Matilda, MatildaConfig

# Initialize Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Set a secret key for session management
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# Configuration
config = MatildaConfig()
matilda_instances = {}

def get_matilda_instance(session_id):
    """Get or create a Matilda instance for the session"""
    if session_id not in matilda_instances:
        matilda_instances[session_id] = Matilda()
    return matilda_instances[session_id]

@app.route('/')
def index():
    """Render the main chat interface"""
    # Generate a unique session ID if not present
    if 'session_id' not in session:
        session['session_id'] = os.urandom(16).hex()
    
    # Initialize Matilda for this session
    matilda = get_matilda_instance(session['session_id'])
    
    # Get user name from environment or config
    username = config.get("username", "User")
    
    return render_template('index.html', 
                          username=username, 
                          assistant_name=config.get("assistant_name", "Matilda"))

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chat interactions"""
    data = request.json
    user_input = data.get('message', '')
    session_id = session.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'No session found'}), 400
    
    # Get Matilda instance for this session
    matilda = get_matilda_instance(session_id)
    
    # Process the user input
    response = matilda.process_input(user_input)
    
    # Get the full conversation history
    history = matilda.conversation.history
    
    return jsonify({
        'response': response,
        'history': history,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/greeting', methods=['GET'])
def greeting():
    """Get the initial greeting from Matilda"""
    session_id = session.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'No session found'}), 400
    
    # Get Matilda instance for this session
    matilda = get_matilda_instance(session_id)
    
    # Get the greeting
    greeting = matilda.startup_greeting()
    
    return jsonify({
        'greeting': greeting,
        'history': matilda.conversation.history,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear the conversation history"""
    session_id = session.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'No session found'}), 400
    
    # Get Matilda instance for this session
    matilda = get_matilda_instance(session_id)
    
    # Clear the conversation history
    matilda.conversation.clear()
    
    return jsonify({
        'status': 'success',
        'message': 'Conversation history cleared'
    })

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    
    print(f"Starting Matilda web interface on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

