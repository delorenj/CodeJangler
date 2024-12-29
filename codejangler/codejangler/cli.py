import os
import click
from crewai import Crew
from crewai.utilities.file_loader import FileLoader

@click.group()
def cli():
    """CodeJangler CLI - Optimize GitHub PRs using AI"""
    pass

@cli.command()
@click.argument('pr_url')
@click.option('--async', 'async_mode', is_flag=True, help='Run optimization asynchronously')
def optimize(pr_url: str, async_mode: bool = False):
    """Analyze and optimize a GitHub PR"""
    # Load crew configuration from YAML
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crew.yaml')
    crew_config = FileLoader.load_crew_from_file(config_path)
    
    # Create crew instance with configuration
    crew = Crew.from_config(crew_config)
    
    # Add PR URL to crew context
    crew.context = {"pr_url": pr_url}
    
    # Run the crew tasks
    if async_mode:
        result = crew.kickoff_async()
    else:
        result = crew.kickoff()
    
    click.echo(result)

if __name__ == '__main__':
    cli()
