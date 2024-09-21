# interfaces/api/fastapi_app.py

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.feature_registry import FeatureRegistry
from features.ai_integration import AIIntegration
from config import AI_PROVIDER, AI_MODEL
from features.file_management import FileManager
from features.bulk_generation import BulkGenerator
from config import PROJECT_ROOT

app = FastAPI()

class CodeGenerationRequest(BaseModel):
    prompt: str
    provider: Optional[str] = AI_PROVIDER
    model: Optional[str] = None

class CodeExplanationRequest(BaseModel):
    code: str
    provider: Optional[str] = AI_PROVIDER
    model: Optional[str] = None

class FileAnalysisRequest(BaseModel):
    file_path: str
    provider: Optional[str] = AI_PROVIDER
    model: Optional[str] = None

class RAGCreationRequest(BaseModel):
    file_path: str
    provider: Optional[str] = AI_PROVIDER
    model: Optional[str] = None

class RAGQueryRequest(BaseModel):
    query: str
    provider: Optional[str] = AI_PROVIDER
    model: Optional[str] = None

class DatasetLoadRequest(BaseModel):
    dataset_path: str
    provider: Optional[str] = AI_PROVIDER
    model: Optional[str] = None

class DatasetAnalysisRequest(BaseModel):
    iterations: int = 1
    row_index: Optional[int] = None
    provider: Optional[str] = AI_PROVIDER
    model: Optional[str] = None

class ProjectGenerationRequest(BaseModel):
    requirement: str
    output_dir: str = '.'
    provider: Optional[str] = AI_PROVIDER
    model: Optional[str] = None

def get_ai_integration(provider: str = AI_PROVIDER, model: Optional[str] = None):
    try:
        return AIIntegration(provider, model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize AI integration: {str(e)}")

@app.post("/generate")
async def generate_code(request: CodeGenerationRequest):
    try:
        ai = get_ai_integration(request.provider, request.model)
        generated_code = ai.generate_code(request.prompt)
        return {"generated_code": generated_code}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/explain")
async def explain_code(request: CodeExplanationRequest):
    try:
        ai = get_ai_integration(request.provider, request.model)
        explanation = ai.explain_code(request.code)
        return {"explanation": explanation}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/analyze")
async def analyze_file(request: FileAnalysisRequest):
    try:
        file_manager = FileManager(PROJECT_ROOT)
        content = file_manager.read_file(request.file_path)
        ai = get_ai_integration(request.provider, request.model)
        analysis = ai.explain_code(content)
        return {"analysis": analysis}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/create-rag")
async def create_rag(request: RAGCreationRequest):
    try:
        ai = get_ai_integration(request.provider, request.model)
        result = ai.create_rag(request.file_path)
        return {"message": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/query-rag")
async def query_rag(request: RAGQueryRequest):
    try:
        ai = get_ai_integration(request.provider, request.model)
        response = ai.query_rag(request.query)
        return {"response": response}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/load-dataset")
async def load_dataset(request: DatasetLoadRequest):
    try:
        ai = get_ai_integration(request.provider, request.model)
        result = ai.load_dataset(request.dataset_path)
        return {"message": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {request.dataset_path}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/analyze-dataset-row")
async def analyze_dataset_row(request: DatasetAnalysisRequest):
    try:
        ai = get_ai_integration(request.provider, request.model)
        if request.row_index is not None:
            row = request.row_index
        else:
            row = ai.dataset.sample(1).iloc[0]
        analysis = ai.analyze_row(row, request.iterations)
        return {"analysis": analysis}
    except IndexError:
        raise HTTPException(status_code=404, detail="Row index out of range")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/generate-project")
async def generate_project(request: ProjectGenerationRequest):
    try:
        ai = get_ai_integration(request.provider, request.model)
        file_manager = FileManager(PROJECT_ROOT)
        generator = BulkGenerator(ai, file_manager)

        analysis = generator.analyze_requirement(request.requirement)
        project_plan = generator.generate_project_plan(request.requirement, analysis['tech_stack'])
        generator.create_project(project_plan, request.output_dir)

        return {
            "message": f"Project generated successfully in {request.output_dir}",
            "analysis": analysis,
            "project_plan": project_plan
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)