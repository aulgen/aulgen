"""Ad Creative Agent - Interviews user and creates scene blueprints."""

import json
from typing import Optional
from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

from ..models.product_info import ProductInfo
from ..models.scene import Scene, SceneBlueprint


class AdCreativeAgent:
    """Agent that interviews the user about their product and creates storytelling scenes."""

    SYSTEM_PROMPT = """You are an expert Ad Creative Director with 20+ years of experience creating
compelling advertising campaigns for global brands. Your specialty is transforming product information
into powerful storytelling that connects emotionally with audiences.

Your role is to:
1. Help users articulate their product/service value proposition
2. Understand their target audience deeply
3. Create a compelling narrative arc for their ad campaign
4. Design specific scenes that tell their story effectively

You are creative, insightful, and always focused on what will resonate with the target audience.
You think visually and understand how to translate concepts into compelling imagery."""

    SCENE_GENERATION_PROMPT = """Based on the following product/service information, create a compelling
ad campaign with a strong storytelling arc.

{product_context}

Create a scene blueprint with:
1. A catchy campaign title
2. An overarching campaign concept (1-2 sentences)
3. A story arc description
4. 4-5 scenes that tell the story, each with:
   - Scene number
   - Title
   - Description (what happens visually)
   - Visual direction (style, mood, colors)
   - Key message to communicate
   - Duration in seconds
   - Story phase (hook, problem, solution, benefit, or cta)

Return your response as a valid JSON object with this structure:
{{
    "campaign_title": "string",
    "campaign_concept": "string",
    "story_arc": "string",
    "scenes": [
        {{
            "scene_number": 1,
            "title": "string",
            "description": "string",
            "visual_direction": "string",
            "key_message": "string",
            "duration_seconds": 5,
            "story_phase": "hook"
        }}
    ],
    "target_platforms": ["Instagram", "Facebook", "YouTube"],
    "total_duration_seconds": 30
}}

Make the campaign emotionally compelling and visually striking. Focus on storytelling that will
resonate with the target audience."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Ad Creative Agent."""
        self.client = Anthropic(api_key=api_key) if api_key else Anthropic()
        self.console = Console()
        self.product_info: Optional[ProductInfo] = None

    def _ask_question(self, question: str, required: bool = True) -> str:
        """Ask the user a question and get their response."""
        self.console.print()
        self.console.print(f"[bold cyan]{question}[/bold cyan]")

        while True:
            response = Prompt.ask("[dim]Your answer[/dim]")
            if response.strip() or not required:
                return response.strip()
            self.console.print("[red]This field is required. Please provide an answer.[/red]")

    def _display_welcome(self):
        """Display welcome message and introduction."""
        welcome = """
# Welcome to the Ad Campaign Designer!

I'm your **Ad Creative Agent**. I'll help you design a compelling advertising campaign
by understanding your product and crafting a storytelling framework.

Let's start by learning about what you're advertising.
"""
        self.console.print(Panel(Markdown(welcome), title="Ad Creative Agent", border_style="cyan"))

    def _display_thinking(self, message: str):
        """Display a thinking/processing message."""
        self.console.print()
        self.console.print(f"[dim italic]{message}[/dim italic]")

    def conduct_interview(self) -> ProductInfo:
        """Conduct the discovery interview with the user."""
        self._display_welcome()

        # Core questions
        name = self._ask_question(
            "What is the name of your product or service?"
        )

        description = self._ask_question(
            "Describe your product/service. What does it do? What problem does it solve?"
        )

        target_audience = self._ask_question(
            "Who is your target audience? (Include demographics, interests, and pain points)"
        )

        benefits_input = self._ask_question(
            "What are the key benefits? (List 3-5 unique selling points, separated by commas)"
        )
        key_benefits = [b.strip() for b in benefits_input.split(",") if b.strip()]

        self.console.print()
        self.console.print("[bold cyan]What emotional tone should the ad convey?[/bold cyan]")
        self.console.print("[dim]Options: inspiring, funny, urgent, heartwarming, bold, sophisticated, playful[/dim]")
        emotional_tone = Prompt.ask(
            "[dim]Your choice[/dim]",
            default="inspiring"
        )

        self.console.print()
        self.console.print("[bold cyan]What is your primary campaign goal?[/bold cyan]")
        self.console.print("[dim]Options: awareness, conversion, engagement, brand building[/dim]")
        campaign_goal = Prompt.ask(
            "[dim]Your choice[/dim]",
            default="awareness"
        )

        self.console.print()
        self.console.print("[bold cyan]What ad format are you planning?[/bold cyan]")
        self.console.print("[dim]Options: video, carousel, single image, story[/dim]")
        ad_format = Prompt.ask(
            "[dim]Your choice[/dim]",
            default="video"
        )

        # Optional questions
        self.console.print()
        self.console.print(Panel("[dim]The following questions are optional. Press Enter to skip.[/dim]"))

        brand_colors = self._ask_question(
            "What are your brand colors? (e.g., 'navy blue and gold')",
            required=False
        ) or None

        brand_voice = self._ask_question(
            "How would you describe your brand voice? (e.g., 'professional but friendly')",
            required=False
        ) or None

        competitors = self._ask_question(
            "Who are your main competitors or how are you positioned in the market?",
            required=False
        ) or None

        additional_notes = self._ask_question(
            "Any additional context or requirements for the campaign?",
            required=False
        ) or None

        self.product_info = ProductInfo(
            name=name,
            description=description,
            target_audience=target_audience,
            key_benefits=key_benefits,
            emotional_tone=emotional_tone,
            campaign_goal=campaign_goal,
            ad_format=ad_format,
            brand_colors=brand_colors,
            brand_voice=brand_voice,
            competitors=competitors,
            additional_notes=additional_notes
        )

        self._display_summary()
        return self.product_info

    def _display_summary(self):
        """Display a summary of collected information."""
        summary = f"""
## Product Information Summary

- **Product/Service:** {self.product_info.name}
- **Description:** {self.product_info.description}
- **Target Audience:** {self.product_info.target_audience}
- **Key Benefits:** {', '.join(self.product_info.key_benefits)}
- **Emotional Tone:** {self.product_info.emotional_tone}
- **Campaign Goal:** {self.product_info.campaign_goal}
- **Ad Format:** {self.product_info.ad_format}
"""
        self.console.print()
        self.console.print(Panel(Markdown(summary), title="Information Collected", border_style="green"))

    def generate_scene_blueprint(self, product_info: Optional[ProductInfo] = None) -> SceneBlueprint:
        """Generate the scene blueprint using Claude."""
        if product_info:
            self.product_info = product_info

        if not self.product_info:
            raise ValueError("No product information available. Run conduct_interview() first.")

        self._display_thinking("Creating your scene blueprint... This may take a moment...")

        prompt = self.SCENE_GENERATION_PROMPT.format(
            product_context=self.product_info.to_prompt_context()
        )

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse the response
        response_text = message.content[0].text

        # Extract JSON from response (handle potential markdown code blocks)
        json_str = response_text
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0]

        blueprint_data = json.loads(json_str.strip())

        # Convert to SceneBlueprint model
        scenes = [Scene(**scene) for scene in blueprint_data.get("scenes", [])]
        blueprint = SceneBlueprint(
            campaign_title=blueprint_data.get("campaign_title", "Untitled Campaign"),
            campaign_concept=blueprint_data.get("campaign_concept", ""),
            story_arc=blueprint_data.get("story_arc", ""),
            scenes=scenes,
            target_platforms=blueprint_data.get("target_platforms", ["Instagram", "Facebook", "YouTube"]),
            total_duration_seconds=blueprint_data.get("total_duration_seconds", 30)
        )

        self._display_blueprint(blueprint)
        return blueprint

    def _display_blueprint(self, blueprint: SceneBlueprint):
        """Display the generated blueprint."""
        self.console.print()
        self.console.print(Panel(
            Markdown(blueprint.to_summary()),
            title="Generated Scene Blueprint",
            border_style="magenta"
        ))

    def run(self) -> SceneBlueprint:
        """Run the complete agent workflow: interview + generate blueprint."""
        self.conduct_interview()
        return self.generate_scene_blueprint()
