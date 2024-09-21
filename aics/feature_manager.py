# feature_manager.py

import click
import importlib
from core.feature_registry import FeatureRegistry

@click.group()
def cli():
    pass

@cli.command()
@click.argument('feature_name')
def add_feature(feature_name):
    """Add a new feature to the project."""
    feature_path = f"features.{feature_name}"
    try:
        module = importlib.import_module(feature_path)
        if hasattr(module, 'setup'):
            module.setup()
        click.echo(f"Feature '{feature_name}' added successfully.")
    except ImportError:
        click.echo(f"Error: Feature '{feature_name}' not found.")

@cli.command()
@click.argument('feature_name')
def remove_feature(feature_name):
    """Remove a feature from the project."""
    if not FeatureRegistry.is_feature_enabled(feature_name):
        click.echo(f"Error: Feature '{feature_name}' is not enabled.")
        return

    dependent_features = FeatureRegistry.get_dependent_features(feature_name)
    if dependent_features:
        click.echo(f"Warning: The following features depend on '{feature_name}':")
        for dep in dependent_features:
            click.echo(f"- {dep}")
        if not click.confirm("Do you want to proceed with removal?"):
            return

    FeatureRegistry._features.pop(feature_name, None)
    click.echo(f"Feature '{feature_name}' removed successfully.")

@cli.command()
def list_features():
    """List all enabled features."""
    features = FeatureRegistry.get_all_features()
    click.echo("Enabled features:")
    for feature in features:
        dependencies = FeatureRegistry.get_feature_dependencies(feature)
        click.echo(f"- {feature}")
        if dependencies:
            click.echo(f"  Dependencies: {', '.join(dependencies)}")

if __name__ == '__main__':
    cli()