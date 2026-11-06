# ZeroCopy-Obs

A no-nonsense code diagnostic engine.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set your API key: `export OPENAI_API_KEY=your_key_here`
3. Run: `uvicorn main:app --reload`

## Usage
POST to `/diagnose` with JSON body:
```json
{
  "language": "python",
  "code": "def foo(): pass",
  "context": "Simple function"
}
```
