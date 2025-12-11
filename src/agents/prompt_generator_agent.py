"""Prompt Generator Agent - Creates image prompts and scripts from scenes."""

import json
from typing import Optional
from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..models.product_info import ProductInfo
from ..models.scene import SceneBlueprint, ScenePrompt, CampaignAssets


class PromptGeneratorAgent:
    """Agent that transforms scene blueprints into actionable image prompts and scripts."""

    SYSTEM_PROMPT = """You are an expert Visual Prompt Engineer and Advertising Copywriter with deep
expertise in AI image generation tools (DALL-E, Midjourney, Stable Diffusion) and compelling ad copy.

Your role is to:
1. Transform scene descriptions into detailed, effective image generation prompts
2. Write compelling scripts and copy that match the visual storytelling
3. Ensure visual consistency across all scenes
4. Create prompts that will generate high-quality, professional advertising imagery

You understand prompt engineering best practices including:
- Specific visual details (lighting, composition, style)
- Mood and atmosphere descriptors
- Camera angles and framing
- Color palettes and visual harmony
- Style references and artistic direction

Your copy is always concise, impactful, and aligned with the campaign's emotional tone."""

    PROMPT_GENERATION_TEMPLATE = """Transform the following scene into an image generation prompt and script.

Campaign Context:
- Title: {campaign_title}
- Concept: {campaign_concept}
- Emotional Tone: {emotional_tone}
- Target Audience: {target_audience}
- Brand Colors: {brand_colors}

Scene Information:
- Scene Number: {scene_number}
- Title: {scene_title}
- Description: {scene_description}
- Visual Direction: {visual_direction}
- Key Message: {key_message}
- Story Phase: {story_phase}
- Duration: {duration}s

Create:
1. A detailed image generation prompt (optimized for AI tools like DALL-E/Midjourney)
2. Script/voiceover text for this scene
3. Visual execution notes
4. Transition recommendation to the next scene

Return your response as a valid JSON object:
{{
    "scene_number": {scene_number},
    "scene_title": "{scene_title}",
    "image_prompt": "detailed prompt for AI image generation...",
    "script": "voiceover or on-screen text...",
    "visual_notes": "additional notes for visual execution...",
    "transition": "cut/fade/dissolve/zoom"
}}

Make the image prompt highly detailed and specific. Include style, lighting, composition, mood, and any relevant artistic direction. The script should be concise and impactful."""

    FULL_SCRIPT_PROMPT = """Based on the following individual scene scripts, create a cohesive full script
that flows naturally from scene to scene.

Campaign: {campaign_title}
Concept: {campaign_concept}

Scene Scripts:
{scene_scripts}

Create a polished, final script that:
1. Flows naturally between scenes
2. Maintains consistent voice and tone
3. Builds to a compelling call-to-action
4. Is ready for voiceover recording or text overlay

Return only the final script text, formatted for easy reading."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Prompt Generator Agent."""
        self.client = Anthropic(api_key=api_key) if api_key else Anthropic()
        self.console = Console()

    def _display_welcome(self, blueprint: SceneBlueprint):
        """Display welcome message."""
        welcome = f"""
# Prompt Generator Agent

I've received your scene blueprint for **"{blueprint.campaign_title}"**.

I'll now transform each of your **{len(blueprint.scenes)} scenes** into:
- Detailed image generation prompts (ready for DALL-E, Midjourney, etc.)
- Compelling scripts and copy
- Visual execution notes
"""
        self.console.print(Panel(Markdown(welcome), title="Prompt Generator Agent", border_style="yellow"))

    def _generate_scene_prompt(
        self,
        scene: 'Scene',
        blueprint: SceneBlueprint,
        product_info: Optional[ProductInfo] = None
    ) -> ScenePrompt:
        """Generate prompts for a single scene."""
        prompt = self.PROMPT_GENERATION_TEMPLATE.format(
            campaign_title=blueprint.campaign_title,
            campaign_concept=blueprint.campaign_concept,
            emotional_tone=product_info.emotional_tone if product_info else "inspiring",
            target_audience=product_info.target_audience if product_info else "general audience",
            brand_colors=product_info.brand_colors if product_info else "not specified",
            scene_number=scene.scene_number,
            scene_title=scene.title,
            scene_description=scene.description,
            visual_direction=scene.visual_direction,
            key_message=scene.key_message,
            story_phase=scene.story_phase,
            duration=scene.duration_seconds
        )

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text

        # Extract JSON from response
        json_str = response_text
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0]

        prompt_data = json.loads(json_str.strip())

        return ScenePrompt(
            scene_number=prompt_data.get("scene_number", scene.scene_number),
            scene_title=prompt_data.get("scene_title", scene.title),
            image_prompt=prompt_data.get("image_prompt", ""),
            script=prompt_data.get("script", ""),
            visual_notes=prompt_data.get("visual_notes", ""),
            transition=prompt_data.get("transition", "cut")
        )

    def _generate_full_script(
        self,
        scene_prompts: list[ScenePrompt],
        blueprint: SceneBlueprint
    ) -> str:
        """Generate the complete cohesive script."""
        scene_scripts = "\n\n".join([
            f"Scene {sp.scene_number} ({sp.scene_title}):\n{sp.script}"
            for sp in scene_prompts
        ])

        prompt = self.FULL_SCRIPT_PROMPT.format(
            campaign_title=blueprint.campaign_title,
            campaign_concept=blueprint.campaign_concept,
            scene_scripts=scene_scripts
        )

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text.strip()

    def generate_campaign_assets(
        self,
        blueprint: SceneBlueprint,
        product_info: Optional[ProductInfo] = None
    ) -> CampaignAssets:
        """Generate all campaign assets from the scene blueprint."""
        self._display_welcome(blueprint)

        scene_prompts = []

        # Generate prompts for each scene with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Generating scene prompts...", total=len(blueprint.scenes))

            for scene in blueprint.scenes:
                progress.update(task, description=f"Processing Scene {scene.scene_number}: {scene.title}...")
                scene_prompt = self._generate_scene_prompt(scene, blueprint, product_info)
                scene_prompts.append(scene_prompt)
                progress.advance(task)

            # Generate full script
            progress.update(task, description="Creating cohesive full script...")
            full_script = self._generate_full_script(scene_prompts, blueprint)

        # Create campaign summary
        campaign_summary = self._create_summary(blueprint, scene_prompts)

        assets = CampaignAssets(
            campaign_title=blueprint.campaign_title,
            scene_prompts=scene_prompts,
            full_script=full_script,
            campaign_summary=campaign_summary
        )

        self._display_results(assets)
        return assets

    def _create_summary(
        self,
        blueprint: SceneBlueprint,
        scene_prompts: list[ScenePrompt]
    ) -> str:
        """Create an executive summary of the campaign."""
        return f"""
# Campaign Summary: {blueprint.campaign_title}

## Concept
{blueprint.campaign_concept}

## Story Arc
{blueprint.story_arc}

## Scene Overview
{len(scene_prompts)} scenes, {blueprint.total_duration_seconds} seconds total

## Target Platforms
{', '.join(blueprint.target_platforms)}

## Assets Generated
- {len(scene_prompts)} Image Generation Prompts
- {len(scene_prompts)} Scene Scripts
- 1 Full Cohesive Script
"""

    def _display_results(self, assets: CampaignAssets):
        """Display the generated results."""
        self.console.print()
        self.console.print(Panel(
            Markdown("## Generation Complete!\n\nYour campaign assets are ready."),
            title="Success",
            border_style="green"
        ))

        # Display each scene prompt
        for prompt in assets.scene_prompts:
            scene_md = f"""
### Scene {prompt.scene_number}: {prompt.scene_title}

**Image Prompt:**
```
{prompt.image_prompt}
```

**Script:**
> {prompt.script}

**Visual Notes:** {prompt.visual_notes}

**Transition:** {prompt.transition}
"""
            self.console.print(Panel(
                Markdown(scene_md),
                title=f"Scene {prompt.scene_number}",
                border_style="blue"
            ))

        # Display full script
        self.console.print(Panel(
            Markdown(f"## Full Script\n\n{assets.full_script}"),
            title="Complete Script",
            border_style="magenta"
        ))

    def run(
        self,
        blueprint: SceneBlueprint,
        product_info: Optional[ProductInfo] = None
    ) -> CampaignAssets:
        """Run the prompt generator workflow."""
        return self.generate_campaign_assets(blueprint, product_info)
