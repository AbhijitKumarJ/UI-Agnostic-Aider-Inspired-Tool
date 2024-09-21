# interfaces/cli/cli_interface.py

import click
from features.bulk_generation import BulkGenerator
from features.ai_integration import AIIntegration
from features.file_management import FileManager
from config import PROJECT_ROOT, AI_PROVIDER, AI_MODEL
from core.feature_registry import FeatureRegistry
import importlib

def load_features():
    for feature_name in FeatureRegistry.get_all_features():
        try:
            importlib.import_module(f"features.{feature_name}")
        except ImportError:
            click.echo(f"Warning: Failed to load feature '{feature_name}'")

@click.group()
@click.pass_context
def cli(ctx):
    load_features()

@cli.command()
@click.argument('file_path')
@click.pass_context
def analyze(ctx, file_path):
    """Analyze a Python file"""
    file_manager = FileManager(PROJECT_ROOT)
    content = file_manager.read_file(file_path)
    provider = ctx.obj.get('provider', AI_PROVIDER)
    model = ctx.obj.get('model', AI_MODEL)
    ai_integration = AIIntegration(provider, model)
    analysis = ai_integration.explain_code(content)
    click.echo(f"Analysis of {file_path}:")
    click.echo(analysis)

@cli.command()
@click.argument('prompt')
@click.pass_context
def generate(ctx, prompt):
    """Generate code based on a prompt"""
    try:
        provider = ctx.obj.get('provider', AI_PROVIDER)
        model = ctx.obj.get('model', AI_MODEL)
        ai_integration = AIIntegration(provider, model)
        code = ai_integration.generate_code(prompt)
        click.echo("Generated code:")
        click.echo(code)
    except ValueError as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}")

@cli.command()
@click.argument('file_path')
@click.pass_context
def explain(ctx, file_path):
    """Explain the code in a file"""
    file_manager = FileManager(PROJECT_ROOT)
    content = file_manager.read_file(file_path)
    provider = ctx.obj.get('provider', AI_PROVIDER)
    model = ctx.obj.get('model', AI_MODEL)
    ai_integration = AIIntegration(provider, model)
    explanation = ai_integration.explain_code(content)
    click.echo(f"Explanation of {file_path}:")
    click.echo(explanation)

@cli.command()
@click.argument('file_path')
@click.pass_context
def create_rag(ctx, file_path):
    """Create a RAG from a file"""
    try:
        provider = ctx.obj.get('provider', AI_PROVIDER)
        model = ctx.obj.get('model', AI_MODEL)
        ai_integration = AIIntegration(provider, model)
        result = ai_integration.create_rag(file_path)
        click.echo(result)
    except ValueError as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}")

@cli.command()
@click.argument('query')
@click.pass_context
def query_rag(ctx, query):
    """Query the saved RAG"""
    try:
        provider = ctx.obj.get('provider', AI_PROVIDER)
        model = ctx.obj.get('model', AI_MODEL)
        ai_integration = AIIntegration(provider, model)
        response = ai_integration.query_rag(query)
        click.echo("RAG response:")
        click.echo(response)
    except ValueError as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}")

@cli.command()
@click.argument('dataset_path')
@click.pass_context
def load_dataset(ctx, dataset_path):
    """Load a dataset for analysis"""
    try:
        provider = ctx.obj.get('provider', AI_PROVIDER)
        model = ctx.obj.get('model', AI_MODEL)
        ai_integration = AIIntegration(provider, model)
        result = ai_integration.load_dataset(dataset_path)
        click.echo(result)
    except ValueError as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}")

@cli.command()
@click.option('--iterations', default=1, help='Number of iterations for analysis')
@click.option('--row-index', default=None, type=int, help='Specific row index to analyze')
@click.pass_context
def analyze_dataset_row(ctx, iterations, row_index):
    """Analyze a row from the loaded dataset"""
    try:
        provider = ctx.obj.get('provider', AI_PROVIDER)
        model = ctx.obj.get('model', AI_MODEL)
        ai_integration = AIIntegration(provider, model)
        if row_index is not None:
            row = row_index
        else:
            row = ai_integration.dataset.sample(1).iloc[0]
        analysis = ai_integration.analyze_row(row, iterations)
        click.echo("Analysis of dataset row:")
        click.echo(analysis)
    except ValueError as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}")

@cli.command()
@click.argument('requirement')
@click.option('--output', '-o', default='.', help='Output directory for the generated project')
@click.pass_context
def generate_project(ctx, requirement, output):
    """Generate a complete project based on the given requirement."""
    ai_integration = AIIntegration(ctx.obj['provider'], ctx.obj['model'])
    file_manager = FileManager(PROJECT_ROOT)
    generator = BulkGenerator(ai_integration, file_manager)

    while True:
        analysis = generator.analyze_requirement(requirement)
        click.echo(f"Understood requirement: {analysis['summary']}")
        click.echo(f"Suggested tech stack: {analysis['tech_stack']}")
        
        if click.confirm("Is this understanding correct?"):
            break
        else:
            requirement = click.prompt("Please provide more details or corrections")

    while True:
        project_plan = generator.generate_project_plan(requirement, analysis['tech_stack'])
        click.echo("Proposed project structure:")
        for file_path in project_plan['files']:
            click.echo(f"  {file_path}")
        
        if click.confirm("Is this project structure acceptable?"):
            break
        else:
            feedback = click.prompt("Please provide feedback on the project structure")
            requirement += f"\n\nAdditional feedback: {feedback}"

    generator.create_project(project_plan, output)
    click.echo(f"Project generated successfully in {output}")

if __name__ == '__main__':
    cli()