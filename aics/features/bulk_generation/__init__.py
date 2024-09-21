import os
from typing import Dict, Any
from features.ai_integration import AIIntegration
from features.file_management import FileManager
from core.feature_registry import FeatureRegistry

@FeatureRegistry.register('bulk_generation', dependencies=['ai_integration', 'file_management'])    
class BulkGenerator:
    def __init__(self, ai_integration: AIIntegration, file_manager: FileManager):
        self.ai = ai_integration
        self.file_manager = file_manager

    def analyze_requirement(self, requirement: str) -> Dict[str, Any]:
        prompt = f"Analyze the following project requirement and suggest a suitable technology stack:\n\n{requirement}\n\nProvide your response in JSON format with 'summary' and 'tech_stack' keys."
        response = self.ai.generate_code(prompt)
        return self._parse_json_response(response)

    def generate_project_plan(self, requirement: str, tech_stack: Dict[str, str]) -> Dict[str, Any]:
        prompt = f"Generate a project plan and file structure for the following requirement using the specified technology stack:\n\nRequirement: {requirement}\n\nTech Stack: {tech_stack}\n\nProvide your response in JSON format with 'files' key containing file paths and descriptions."
        response = self.ai.generate_code(prompt)
        return self._parse_json_response(response)

    def generate_file_content(self, file_path: str, file_description: str) -> str:
        prompt = f"Generate the content for the following file:\n\nFile: {file_path}\nDescription: {file_description}\n\nProvide only the file content in your response."
        return self.ai.generate_code(prompt)

    def create_project(self, project_plan: Dict[str, Any], output_dir: str):
        for file_path, file_description in project_plan['files'].items():
            content = self.generate_file_content(file_path, file_description)
            full_path = os.path.join(output_dir, file_path)
            self.file_manager.write_file(full_path, content)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        try:
            import json
            return json.loads(response)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse AI response as JSON")
