#!/usr/bin/env python
import sys
import warnings

from pr_optimizer.crew import PrOptimizer

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

import click

@click.group()
def cli():
    """CodeJangler CLI - Optimize GitHub PRs using AI"""
    pass

@cli.command()
@click.argument('pr_url')
@click.option('--async', 'async_mode', is_flag=True, help='Run optimization asynchronously')
def optimize(pr_url: str, async_mode: bool = False):
    """Analyze and optimize a GitHub PR"""
    try:
        inputs = {
            'pr_url': pr_url,
            'async_mode': async_mode
        }
        
        if async_mode:
            PrOptimizer().crew().kickoff_async(inputs=inputs)
        else:
            PrOptimizer().crew().kickoff(inputs=inputs)
            
    except Exception as e:
        raise click.ClickException(f"Failed to optimize PR: {str(e)}")

@cli.command()
@click.argument('pr_url')
@click.option('--iterations', '-n', default=1, help='Number of training iterations')
@click.option('--output', '-o', required=True, help='Output file for training data')
def train(pr_url: str, iterations: int, output: str):
    """Train the crew with a sample PR"""
    try:
        inputs = {'pr_url': pr_url}
        PrOptimizer().crew().train(
            n_iterations=iterations,
            filename=output,
            inputs=inputs
        )
    except Exception as e:
        raise click.ClickException(f"Training failed: {str(e)}")

@cli.command()
@click.argument('task_id')
def replay(task_id: str):
    """Replay the crew execution from a specific task"""
    try:
        PrOptimizer().crew().replay(task_id=task_id)
    except Exception as e:
        raise click.ClickException(f"Replay failed: {str(e)}")

@cli.command()
@click.argument('pr_url')
@click.option('--iterations', '-n', default=1, help='Number of test iterations')
@click.option('--model', required=True, help='Model to use for testing')
def test(pr_url: str, iterations: int, model: str):
    """Test the crew execution and return results"""
    try:
        inputs = {'pr_url': pr_url}
        PrOptimizer().crew().test(
            n_iterations=iterations,
            openai_model_name=model,
            inputs=inputs
        )
    except Exception as e:
        raise click.ClickException(f"Testing failed: {str(e)}")

if __name__ == '__main__':
    cli()
