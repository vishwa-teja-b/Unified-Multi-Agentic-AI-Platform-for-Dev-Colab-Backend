from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import httpx
import subprocess
import os
import tempfile
import asyncio
from typing import List, Optional
from app.config.external_services import PISTON_API_URL

router = APIRouter(prefix="/api/execution", tags=["Code Execution"])

class FileContent(BaseModel):
    name: str
    content: str

class ExecutionRequest(BaseModel):
    language: str
    version: str = "*" 
    files: List[FileContent]
    stdin: Optional[str] = ""
    args: Optional[List[str]] = []
    compile_timeout: int = 10000
    run_timeout: int = 3000

class ExecutionResponse(BaseModel):
    run: dict
    compile: Optional[dict] = None
    language: str
    version: str

@router.post("", response_model=ExecutionResponse)
async def execute_code(request: ExecutionRequest):
    """
    Execute code using the Self-Hosted Piston API (Docker).
    """
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "language": request.language,
                "version": request.version,
                "files": [f.model_dump() for f in request.files],
                "stdin": request.stdin,
                "args": request.args,
                "compile_timeout": request.compile_timeout,
                "run_timeout": request.run_timeout,
            }
            
            print(f"Executing Code (Self-Hosted): {payload}")
            
            # Forward directly to local Piston service
            response = await client.post(PISTON_API_URL, json=payload)
            
            if response.status_code != 200:
                print(f"Piston Error Body: {response.text}")

            response.raise_for_status()
            return response.json()
            
        except httpx.ConnectError:
             raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Code Execution Service (Piston) is unavailable. Please ensure Docker container is running."
            )
        except httpx.HTTPStatusError as e:
            print(f"HTTPStatusError: {e}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Piston API Error: {e.response.text}"
            )
        except Exception as e:
            print(f"Exception: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
