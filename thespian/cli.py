"""
Command-line interface for the Thespian framework.
"""

import click
from pathlib import Path
from .theatre import Theatre
from .production import Production
from .llm.playwright import EnhancedPlaywright
from .llm import LLMManager
from .llm.theatrical_memory import TheatricalMemory
from .llm.quality_control import TheatricalQualityControl
from .llm.theatrical_advisors import AdvisorManager
from .llm.run_manager import RunManager
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Thespian CLI - AI-Driven Theatrical Production"""
    pass

@cli.command()
@click.option('--theme', required=True, help='Theme or concept for the production')
@click.option('--output-file', required=True, help='Output file path')
@click.option('--setting', default="Modern Day", help='Setting for the play')
@click.option('--style', default="Contemporary Drama", help='Style of the play')
@click.option('--period', default="Present Day", help='Time period of the play')
@click.option('--target-audience', default="General Audience", help='Target audience')
def create_production(theme, output_file, setting, style, period, target_audience):
    """Create a new theatrical production."""
    try:
        # Initialize components
        llm_manager = LLMManager()
        memory = TheatricalMemory()
        advisor_manager = AdvisorManager(llm_manager, memory)
        quality_control = TheatricalQualityControl()
        run_manager = RunManager()

        # Create playwright
        playwright = EnhancedPlaywright(
            name="Professional Playwright",
            llm_manager=llm_manager,
            memory=memory,
            advisor_manager=advisor_manager,
            quality_control=quality_control
        )

        # Create a new run
        run_id = str(uuid.uuid4())
        run_manager.start_run(run_id)

        # Define base requirements
        base_requirements = {
            "setting": setting,
            "characters": [],  # Will be populated by the playwright
            "props": [],  # Will be populated by the playwright
            "lighting": "Standard theatrical",
            "sound": "Standard theatrical",
            "style": style,
            "period": period,
            "target_audience": target_audience
        }

        # Save initial metadata
        run_manager.save_artifact(run_id, "metadata", {
            "title": theme,
            "requirements": base_requirements,
            "start_time": datetime.now().isoformat()
        })

        # Initialize story outline
        story_outline = playwright.create_story_outline(theme, base_requirements)
        playwright.story_outline = story_outline

        # Generate the full production
        production = playwright.generate_full_production(
            theme=theme,
            requirements=base_requirements,
            run_manager=run_manager,
            run_id=run_id
        )

        # Save the production to file
        output_path = Path(output_file)
        with output_path.open('w') as f:
            f.write(production.to_markdown())

        click.echo(f"\nProduction details saved to: {output_file}")

    except Exception as e:
        logger.error(f"Error creating production: {str(e)}")
        if 'run_id' in locals():
            run_manager.save_error(run_id, e, {
                "stage": "production_creation",
                "fatal": True
            })
            run_manager.update_run_status(run_id, "failed", {
                "end_time": datetime.now().isoformat(),
                "error": str(e)
            })
        raise click.ClickException(str(e))

@cli.command()
@click.argument('production_file')
def perform(production_file):
    """Perform a theatrical production."""
    theatre = Theatre()
    production = Production.from_file(production_file)
    theatre.perform(production)

@cli.command()
def list_productions():
    """List all available productions."""
    productions_dir = Path('productions')
    if not productions_dir.exists():
        click.echo("No productions found.")
        return

    for production_file in productions_dir.glob('*.txt'):
        click.echo(f"- {production_file.stem}")

if __name__ == '__main__':
    cli()
