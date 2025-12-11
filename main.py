#!/usr/bin/env python3
"""
Ad Campaign Designer Team

A multi-agent application that helps create compelling ad campaigns through
guided storytelling and AI-powered prompt generation.

Agents:
1. Ad Creative Agent - Interviews you about your product and creates scene blueprints
2. Prompt Generator Agent - Creates image prompts and scripts from scenes

Usage:
    python main.py              # Interactive mode (requires terminal input)
    python main.py --demo       # Demo mode with sample product data
"""

import argparse
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Confirm

from src.agents.ad_creative_agent import AdCreativeAgent
from src.agents.prompt_generator_agent import PromptGeneratorAgent
from src.models.product_info import ProductInfo
from src.utils.formatters import OutputFormatter


def display_header(console: Console):
    """Display the application header."""
    header = """
# Ad Campaign Designer Team

Welcome to your creative AI team for designing ad campaigns!

## How It Works

1. **Ad Creative Agent** will interview you about your product/service
2. Based on your answers, it creates a storytelling scene blueprint
3. **Prompt Generator Agent** transforms scenes into:
   - Image generation prompts (for DALL-E, Midjourney, etc.)
   - Scripts and copy for your ads

Let's create something amazing!
"""
    console.print(Panel(Markdown(header), border_style="bold blue"))


def display_footer(console: Console, output_folder: Path):
    """Display the completion footer."""
    footer = f"""
# Campaign Complete!

Your ad campaign assets have been saved to:
`{output_folder}`

## Next Steps

1. **Generate Images**: Use the prompts in `image_prompts.md` with your preferred AI image tool
2. **Record Voiceover**: Use `campaign_script.md` for voiceover recording
3. **Assemble**: Combine images and audio in your video editor
4. **Launch**: Deploy your campaign across your target platforms!

Thank you for using Ad Campaign Designer Team!
"""
    console.print(Panel(Markdown(footer), border_style="bold green"))


def get_demo_product_info() -> ProductInfo:
    """Return sample product info for demo mode."""
    return ProductInfo(
        name="EcoBreeze Smart Water Bottle",
        description="A smart water bottle that tracks hydration, keeps drinks cold for 24 hours, "
                    "and reminds you to drink water throughout the day via a companion app. "
                    "Made from 100% recycled ocean plastic.",
        target_audience="Health-conscious millennials and Gen Z (ages 22-38) who care about "
                       "sustainability, use fitness apps, and are willing to pay premium for "
                       "eco-friendly products. They experience dehydration from busy lifestyles.",
        key_benefits=[
            "Tracks daily water intake automatically",
            "24-hour cold / 12-hour hot insulation",
            "Made from recycled ocean plastic",
            "Smart reminders via app",
            "Sleek, Instagram-worthy design"
        ],
        emotional_tone="inspiring",
        campaign_goal="awareness",
        ad_format="video",
        brand_colors="ocean blue and white",
        brand_voice="friendly, motivational, eco-conscious",
        competitors="Positioned against HydroFlask and S'well as the smart, sustainable alternative",
        additional_notes="Launch campaign for Earth Day. Want to emphasize the ocean plastic story."
    )


def run_demo_mode(api_key: str, console: Console):
    """Run the application in demo mode with sample data."""
    console.print()
    console.print(Panel(
        "[bold yellow]DEMO MODE[/bold yellow]\n\n"
        "Running with sample product: EcoBreeze Smart Water Bottle\n"
        "A smart, sustainable water bottle made from recycled ocean plastic.",
        border_style="yellow"
    ))

    # Get demo product info
    product_info = get_demo_product_info()

    # Display the product info
    console.print()
    console.print(Panel(
        Markdown(f"""
## Demo Product Information

- **Product:** {product_info.name}
- **Description:** {product_info.description}
- **Target Audience:** {product_info.target_audience}
- **Key Benefits:** {', '.join(product_info.key_benefits)}
- **Emotional Tone:** {product_info.emotional_tone}
- **Campaign Goal:** {product_info.campaign_goal}
- **Ad Format:** {product_info.ad_format}
"""),
        title="Product Info (Sample)",
        border_style="green"
    ))

    # Initialize agents
    ad_creative_agent = AdCreativeAgent(api_key=api_key)
    prompt_generator_agent = PromptGeneratorAgent(api_key=api_key)
    output_formatter = OutputFormatter()

    # Phase 1: Generate scene blueprint
    console.print()
    console.print("[bold]Phase 1: Scene Blueprint Generation[/bold]")
    console.print("-" * 40)

    blueprint = ad_creative_agent.generate_scene_blueprint(product_info)

    # Phase 2: Generate prompts and scripts
    console.print()
    console.print("[bold]Phase 2: Prompt & Script Generation[/bold]")
    console.print("-" * 40)

    campaign_assets = prompt_generator_agent.run(blueprint, product_info)

    # Save outputs
    console.print()
    console.print("[bold]Saving Campaign Assets...[/bold]")
    output_folder = output_formatter.save_campaign(
        assets=campaign_assets,
        blueprint=blueprint,
        product_info=product_info
    )

    return output_folder


def run_interactive_mode(api_key: str, console: Console):
    """Run the application in interactive mode."""
    # Initialize agents
    ad_creative_agent = AdCreativeAgent(api_key=api_key)
    prompt_generator_agent = PromptGeneratorAgent(api_key=api_key)
    output_formatter = OutputFormatter()

    # Phase 1: Ad Creative Agent interviews user and creates blueprint
    console.print()
    console.print("[bold]Phase 1: Discovery & Scene Creation[/bold]")
    console.print("-" * 40)

    product_info = ad_creative_agent.conduct_interview()
    blueprint = ad_creative_agent.generate_scene_blueprint()

    # Ask to continue
    console.print()
    if not Confirm.ask("Would you like to proceed with generating image prompts and scripts?"):
        console.print("[yellow]Campaign paused. You can restart to continue.[/yellow]")
        sys.exit(0)

    # Phase 2: Prompt Generator creates prompts and scripts
    console.print()
    console.print("[bold]Phase 2: Prompt & Script Generation[/bold]")
    console.print("-" * 40)

    campaign_assets = prompt_generator_agent.run(blueprint, product_info)

    # Save outputs
    console.print()
    console.print("[bold]Saving Campaign Assets...[/bold]")
    output_folder = output_formatter.save_campaign(
        assets=campaign_assets,
        blueprint=blueprint,
        product_info=product_info
    )

    return output_folder


def main():
    """Main entry point for the Ad Campaign Designer Team."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Ad Campaign Designer Team")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with sample product data"
    )
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        console = Console()
        console.print("[red]Error: ANTHROPIC_API_KEY environment variable is not set.[/red]")
        console.print("\nPlease set your API key:")
        console.print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        console.print("\nOr create a .env file with:")
        console.print("  ANTHROPIC_API_KEY=your-api-key-here")
        sys.exit(1)

    console = Console()

    try:
        # Display header
        display_header(console)

        # Run appropriate mode
        if args.demo:
            output_folder = run_demo_mode(api_key, console)
        else:
            output_folder = run_interactive_mode(api_key, console)

        # Display footer
        display_footer(console, output_folder)

    except KeyboardInterrupt:
        console.print("\n[yellow]Campaign creation interrupted. Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]An error occurred: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
