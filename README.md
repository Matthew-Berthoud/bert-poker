# bert-poker
Poker Web App

## Development Environment Setup
```
source .venv/bin/activate
pip install Flask
pip install flask-socketio

deactivate
```

## Plans / Notes
* use the built-in message or json events, but with various namespaces for the different events
    * Always use send, not emit, since send is for unnamed (built-in) events, and emit is for custom

