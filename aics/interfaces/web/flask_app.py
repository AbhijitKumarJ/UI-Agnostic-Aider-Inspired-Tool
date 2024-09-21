# interfaces/web/flask_app.py

from flask import Flask, render_template, request, jsonify
from core.feature_registry import FeatureRegistry
from features.ai_integration import AIIntegration
from config import AI_PROVIDER, AI_MODEL, PROJECT_ROOT
from features.file_management import FileManager
from features.bulk_generation import BulkGenerator

app = Flask(__name__)

def get_ai_integration(provider=AI_PROVIDER, model=None):
    try:
        return AIIntegration(provider, model)
    except Exception as e:
        raise ValueError(f"Failed to initialize AI integration: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_code():
    prompt = request.form['prompt']
    provider = request.form.get('provider', AI_PROVIDER)
    model = request.form.get('model')

    try:
        ai = get_ai_integration(provider, model)
        code = ai.generate_code(prompt)
        return jsonify({"generated_code": code})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/explain', methods=['POST'])
def explain_code():
    code = request.form['code']
    provider = request.form.get('provider', AI_PROVIDER)
    model = request.form.get('model')

    try:
        ai = get_ai_integration(provider, model)
        explanation = ai.explain_code(code)
        return jsonify({"explanation": explanation})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/analyze', methods=['POST'])
def analyze_file():
    file_path = request.form['file_path']
    provider = request.form.get('provider', AI_PROVIDER)
    model = request.form.get('model')

    try:
        ai = get_ai_integration(provider, model)
        file_manager = FileManager(PROJECT_ROOT)
        content = file_manager.read_file(file_path)
        analysis = ai.explain_code(content)
        return jsonify({"analysis": analysis})
    except FileNotFoundError:
        return jsonify({"error": f"File not found: {file_path}"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/create-rag', methods=['POST'])
def create_rag():
    file_path = request.form['file_path']
    provider = request.form.get('provider', AI_PROVIDER)
    model = request.form.get('model')

    try:
        ai = get_ai_integration(provider, model)
        result = ai.create_rag(file_path)
        return jsonify({"message": result})
    except FileNotFoundError:
        return jsonify({"error": f"File not found: {file_path}"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/query-rag', methods=['POST'])
def query_rag():
    query = request.form['query']
    provider = request.form.get('provider', AI_PROVIDER)
    model = request.form.get('model')

    try:
        ai = get_ai_integration(provider, model)
        response = ai.query_rag(query)
        return jsonify({"response": response})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/load-dataset', methods=['POST'])
def load_dataset():
    dataset_path = request.form['dataset_path']
    provider = request.form.get('provider', AI_PROVIDER)
    model = request.form.get('model')

    try:
        ai = get_ai_integration(provider, model)
        result = ai.load_dataset(dataset_path)
        return jsonify({"message": result})
    except FileNotFoundError:
        return jsonify({"error": f"Dataset not found: {dataset_path}"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/analyze-dataset-row', methods=['POST'])
def analyze_dataset_row():
    iterations = int(request.form.get('iterations', 1))
    row_index = request.form.get('row_index')
    if row_index is not None:
        row_index = int(row_index)
    provider = request.form.get('provider', AI_PROVIDER)
    model = request.form.get('model')

    try:
        ai = get_ai_integration(provider, model)
        if row_index is not None:
            row = row_index
        else:
            row = ai.dataset.sample(1).iloc[0]
        analysis = ai.analyze_row(row, iterations)
        return jsonify({"analysis": analysis})
    except IndexError:
        return jsonify({"error": "Row index out of range"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/generate-project', methods=['POST'])
def generate_project():
    requirement = request.form['requirement']
    output_dir = request.form.get('output_dir', '.')
    provider = request.form.get('provider', AI_PROVIDER)
    model = request.form.get('model')

    try:
        ai = get_ai_integration(provider, model)
        file_manager = FileManager(PROJECT_ROOT)
        generator = BulkGenerator(ai, file_manager)

        analysis = generator.analyze_requirement(requirement)
        project_plan = generator.generate_project_plan(requirement, analysis['tech_stack'])
        generator.create_project(project_plan, output_dir)

        return jsonify({
            "message": f"Project generated successfully in {output_dir}",
            "analysis": analysis,
            "project_plan": project_plan
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)