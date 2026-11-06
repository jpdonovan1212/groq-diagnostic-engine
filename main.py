import os
import yaml
import logging
from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, validator
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

app = FastAPI(title="ZeroCopy-Obs Diagnostic Engine")

# Initialize Client Singleton
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class CodeRequest(BaseModel):
    language: str = Field(..., description="Programming language of the code")
    code: str = Field(..., description="Source code to diagnose")
    context: Optional[str] = Field(None, description="Additional context")

    @validator('code')
    def code_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Code cannot be empty')
        return v

@app.post("/diagnose")
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def diagnose_code(req: CodeRequest):
    """
    Forces the AI to act as a ruthless auditor.
    """
    system_msg = config.get("system_prompt", "")
    
    # Sanitize input to prevent prompt injection and encoding issues
    safe_context = req.context.replace("\u00A0", " ").replace("`", "") if req.context else ""
    safe_code = req.code.replace("\u00A0", " ").replace("`", "")
    
    user_msg = f"""
Language: {req.language}
Context: {safe_context}

Code:
{safe_code}
"""

    try:
        response = await client.chat.completions.create(
            model=config["model"],
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=config.get("temperature", 0.1),
            max_tokens=config.get("max_tokens", 500)
        )
        
        result = response.choices[0].message.content.strip()
        
        # Basic sanity check on output format
        if result not in ["CLEAN"] and not result.startswith("[ERROR"):
            logging.warning(f"Model output deviated from expected format: {result}")
            
        return {"result": result}
    
    except Exception as e:
        logging.error(f"Diagnosis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
