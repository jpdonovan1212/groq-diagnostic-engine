import subprocess
import tempfile
import os
import json
import requests
import time

def run_sandbox(code: str, language: str) -> dict:
    """
    Runs code in a sandboxed environment and returns execution results.
    """
    temp_dir = tempfile.mkdtemp()
    file_path = None
    
    try:
        if language == "python":
            file_path = os.path.join(temp_dir, "script.py")
            with open(file_path, "w") as f:
                f.write(code)
            
            result = subprocess.run(
                ["python", file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error_found": result.returncode != 0
            }
        
        elif language == "javascript":
            file_path = os.path.join(temp_dir, "script.js")
            with open(file_path, "w") as f:
                f.write(code)
            
            result = subprocess.run(
                ["node", file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error_found": result.returncode != 0
            }
            
        else:
            return {"error": f"Unsupported language: {language}"}
            
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        os.rmdir(temp_dir)

def feedback_loop():
    """
    Runs a feedback loop by sending code to the engine and comparing results.
    """
    api_url = "http://localhost:8000/diagnose"
    
    # Example Python code with an error
    test_code = """
def foo():
    x = 1 / 0
    print(x)
"""
    
    payload = {
        "language": "python",
        "code": test_code,
        "context": "Simple function"
    }
    
    # Get diagnosis from ZeroCopy-Obs
    response = requests.post(api_url, json=payload)
    ai_diagnosis = response.json().get("result", "")
    
    # Run sandbox
    sandbox_result = run_sandbox(test_code, "python")
    
    # Compare results
    ai_has_error = "[ERROR]" in ai_diagnosis
    actual_has_error = sandbox_result.get("error_found", False)
    
    if ai_has_error == actual_has_error:
        status = "CORRECT"
    else:
        status = "INCORRECT"
        
    print(json.dumps({
        "ai_diagnosis": ai_diagnosis,
        "sandbox_result": sandbox_result,
        "status": status
    }, indent=2))

if __name__ == "__main__":
    feedback_loop()
