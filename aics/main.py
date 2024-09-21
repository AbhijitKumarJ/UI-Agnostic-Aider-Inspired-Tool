# main.py

import click
import os
from interfaces.cli.cli_interface import cli as cli_interface
import uvicorn
from interfaces.api.fastapi_app import app as fastapi_app
from interfaces.web.flask_app import app as flask_app
from core.feature_registry import FeatureRegistry
from config import AI_PROVIDER, AI_MODEL

@click.group()
@click.option('--provider', default=AI_PROVIDER, help='AI provider to use (groq, openrouter, ollama)')
@click.option('--model', default=None, help='Model to use for the selected provider')
@click.pass_context
def main(ctx, provider, model):
    ctx.ensure_object(dict)
    ctx.obj['provider'] = provider
    ctx.obj['model'] = model

main.add_command(cli_interface, name="cli")

@main.command()
@click.option('--port', default=8000, help='Port to run the API server on')
def api(port):
    """Run the FastAPI server"""
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port)

@main.command()
@click.option('--port', default=5000, help='Port to run the web server on')
def web(port):
    """Run the Flask web server"""
    flask_app.run(host="0.0.0.0", port=port, debug=True)

@main.group()
@click.pass_context
def feature(ctx):
    """Feature-specific commands"""
    pass

# Dynamically add feature commands
for feature_name in FeatureRegistry.get_all_features():
    @feature.command(name=feature_name)
    @click.pass_context
    @click.argument('action', type=click.Choice(['run', 'info']))
    @click.option('--args', '-a', multiple=True, help='Arguments to pass to the feature')
    def feature_command(ctx, action, args, feature_name=feature_name):
        provider = ctx.obj.get('provider', AI_PROVIDER)
        model = ctx.obj.get('model', AI_MODEL)
        feature_class = FeatureRegistry.get_feature(feature_name)
        if not feature_class:
            click.echo(f"Error: Feature '{feature_name}' not found.")
            return
        feature_instance = feature_class(provider, model)
        if action == 'run':
            if hasattr(feature_instance, 'run'):
                feature_instance.run(*args)
            else:
                click.echo(f"Error: Feature '{feature_name}' does not have a 'run' method.")
        elif action == 'info':
            if hasattr(feature_instance, 'info'):
                feature_instance.info()
            else:
                click.echo(f"Error: Feature '{feature_name}' does not have an 'info' method.")

if __name__ == '__main__':
    main(obj={})