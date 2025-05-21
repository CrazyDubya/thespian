"""
Test script for LLM integration in Thespian framework.
"""

import os
from thespian.llm import LLMManager
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

console = Console()


def test_llm_integration():
    """Test the LLM integration with both Ollama and Grok models."""

    # Initialize LLM manager
    llm_manager = LLMManager()

    # Test prompts
    test_prompts = [
        "Write a short monologue about the beauty of theater.",
        "Describe a dramatic scene in three sentences.",
        "What makes a great theatrical performance?",
    ]

    # Test with different agent IDs to ensure distribution
    agent_ids = ["playwright_1", "director_1", "actor_1"]

    console.print(
        Panel.fit(
            "[bold blue]Testing LLM Integration[/bold blue]\n\n"
            "Using:\n"
            f"- Ollama ({llm_manager.config.ollama_model})\n"
            f"- Grok ({llm_manager.config.grok_model})",
            title="Thespian LLM Test",
            border_style="blue",
        )
    )

    for prompt_idx, prompt in enumerate(test_prompts, 1):
        console.print(f"\n[bold yellow]Test Prompt {prompt_idx}:[/bold yellow]")
        console.print(Panel(prompt, style="yellow"))

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Agent")
        table.add_column("Model")
        table.add_column("Response")

        for agent_id in agent_ids:
            try:
                # Get model info before generating response
                model_info = llm_manager.get_model_info(agent_id)
                model_type = model_info["type"].capitalize()

                # Generate response
                result = llm_manager.generate_response(prompt, agent_id)

                # Add result to table
                table.add_row(
                    f"[cyan]{agent_id}[/cyan]", f"[green]{model_type}[/green]", result["response"]
                )
            except Exception as e:
                table.add_row(
                    f"[cyan]{agent_id}[/cyan]",
                    f"[red]{model_type}[/red]",
                    f"[red]Error: {str(e)}[/red]",
                )

        console.print(table)
        console.print("\n" + "=" * 80)


if __name__ == "__main__":
    test_llm_integration()
