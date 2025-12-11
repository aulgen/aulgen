"""Output formatting utilities for campaign assets."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console

from ..models.product_info import ProductInfo
from ..models.scene import SceneBlueprint, CampaignAssets


class OutputFormatter:
    """Handles saving and formatting campaign outputs."""

    def __init__(self, output_dir: str = "output"):
        """Initialize the formatter with an output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.console = Console()

    def _create_campaign_folder(self, campaign_title: str) -> Path:
        """Create a folder for the campaign outputs."""
        # Clean the title for use as folder name
        clean_title = "".join(c for c in campaign_title if c.isalnum() or c in (' ', '-', '_'))
        clean_title = clean_title.replace(' ', '_').lower()

        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{clean_title}_{timestamp}"

        campaign_folder = self.output_dir / folder_name
        campaign_folder.mkdir(parents=True, exist_ok=True)

        return campaign_folder

    def save_campaign(
        self,
        assets: CampaignAssets,
        blueprint: SceneBlueprint,
        product_info: Optional[ProductInfo] = None
    ) -> Path:
        """Save all campaign assets to files."""
        folder = self._create_campaign_folder(assets.campaign_title)

        # Save image prompts document
        prompts_path = folder / "image_prompts.md"
        with open(prompts_path, 'w') as f:
            f.write(assets.to_image_prompts_document())

        # Save script document
        script_path = folder / "campaign_script.md"
        with open(script_path, 'w') as f:
            f.write(assets.to_script_document())

        # Save scene blueprint
        blueprint_path = folder / "scene_blueprint.md"
        with open(blueprint_path, 'w') as f:
            f.write(blueprint.to_summary())

        # Save campaign summary
        summary_path = folder / "campaign_summary.md"
        with open(summary_path, 'w') as f:
            f.write(assets.campaign_summary)

        # Save product info if available
        if product_info:
            product_path = folder / "product_info.md"
            with open(product_path, 'w') as f:
                f.write("# Product Information\n\n")
                f.write(product_info.to_prompt_context())

        # Save raw data as JSON for potential reuse
        import json

        data_path = folder / "campaign_data.json"
        campaign_data = {
            "campaign_title": assets.campaign_title,
            "blueprint": {
                "campaign_title": blueprint.campaign_title,
                "campaign_concept": blueprint.campaign_concept,
                "story_arc": blueprint.story_arc,
                "scenes": [s.model_dump() for s in blueprint.scenes],
                "target_platforms": blueprint.target_platforms,
                "total_duration_seconds": blueprint.total_duration_seconds
            },
            "scene_prompts": [sp.model_dump() for sp in assets.scene_prompts],
            "full_script": assets.full_script
        }
        if product_info:
            campaign_data["product_info"] = product_info.model_dump()

        with open(data_path, 'w') as f:
            json.dump(campaign_data, f, indent=2)

        self._display_save_summary(folder)
        return folder

    def _display_save_summary(self, folder: Path):
        """Display information about saved files."""
        from rich.panel import Panel
        from rich.markdown import Markdown

        files = list(folder.glob("*"))
        file_list = "\n".join([f"- `{f.name}`" for f in files])

        summary = f"""
## Campaign Assets Saved!

**Location:** `{folder}`

**Files Generated:**
{file_list}

You can now use the image prompts with AI image generators like:
- DALL-E (OpenAI)
- Midjourney
- Stable Diffusion
- Leonardo.ai
"""
        self.console.print()
        self.console.print(Panel(Markdown(summary), title="Files Saved", border_style="green"))
