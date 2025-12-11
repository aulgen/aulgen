"""Scene and campaign blueprint models."""

from typing import Optional
from pydantic import BaseModel, Field


class Scene(BaseModel):
    """Represents a single scene in the ad campaign story."""

    scene_number: int = Field(
        description="Order of the scene in the story"
    )
    title: str = Field(
        description="Short title for the scene"
    )
    description: str = Field(
        description="Detailed description of what happens in this scene"
    )
    visual_direction: str = Field(
        description="Visual style, composition, colors, and mood"
    )
    key_message: str = Field(
        description="The main message this scene should communicate"
    )
    duration_seconds: Optional[int] = Field(
        default=5,
        description="Recommended duration in seconds (for video)"
    )
    story_phase: str = Field(
        default="middle",
        description="Phase in story arc: hook, problem, solution, benefit, or cta"
    )


class ScenePrompt(BaseModel):
    """Generated prompts and scripts for a scene."""

    scene_number: int = Field(
        description="Reference to the original scene number"
    )
    scene_title: str = Field(
        description="Title of the scene"
    )
    image_prompt: str = Field(
        description="Detailed prompt for AI image generation"
    )
    script: str = Field(
        description="Voiceover or on-screen text for this scene"
    )
    visual_notes: str = Field(
        description="Additional notes for visual execution"
    )
    transition: str = Field(
        default="cut",
        description="Transition to next scene (cut, fade, dissolve, zoom)"
    )


class SceneBlueprint(BaseModel):
    """Complete scene blueprint from the Ad Creative Agent."""

    campaign_title: str = Field(
        description="Overall title for the ad campaign"
    )
    campaign_concept: str = Field(
        description="High-level concept and theme"
    )
    story_arc: str = Field(
        description="Description of the narrative arc"
    )
    scenes: list[Scene] = Field(
        default_factory=list,
        description="List of scenes in order"
    )
    target_platforms: list[str] = Field(
        default_factory=lambda: ["Instagram", "Facebook", "YouTube"],
        description="Recommended platforms for this campaign"
    )
    total_duration_seconds: Optional[int] = Field(
        default=30,
        description="Total recommended duration"
    )

    def to_summary(self) -> str:
        """Create a readable summary of the blueprint."""
        summary = f"""
# {self.campaign_title}

## Concept
{self.campaign_concept}

## Story Arc
{self.story_arc}

## Scenes ({len(self.scenes)} total)
"""
        for scene in self.scenes:
            summary += f"""
### Scene {scene.scene_number}: {scene.title}
- **Phase:** {scene.story_phase}
- **Description:** {scene.description}
- **Visual Direction:** {scene.visual_direction}
- **Key Message:** {scene.key_message}
- **Duration:** {scene.duration_seconds}s
"""

        summary += f"\n## Target Platforms\n{', '.join(self.target_platforms)}"
        summary += f"\n\n## Total Duration\n{self.total_duration_seconds} seconds"

        return summary


class CampaignAssets(BaseModel):
    """Complete campaign assets from the Prompt Generator Agent."""

    campaign_title: str = Field(
        description="Title of the campaign"
    )
    scene_prompts: list[ScenePrompt] = Field(
        default_factory=list,
        description="Generated prompts for each scene"
    )
    full_script: str = Field(
        description="Complete script combining all scenes"
    )
    campaign_summary: str = Field(
        description="Executive summary of the campaign"
    )

    def to_image_prompts_document(self) -> str:
        """Generate a document with all image prompts."""
        doc = f"# Image Prompts for: {self.campaign_title}\n\n"
        doc += "Use these prompts with AI image generators like DALL-E, Midjourney, or Stable Diffusion.\n\n"
        doc += "---\n\n"

        for prompt in self.scene_prompts:
            doc += f"## Scene {prompt.scene_number}: {prompt.scene_title}\n\n"
            doc += f"### Image Generation Prompt\n```\n{prompt.image_prompt}\n```\n\n"
            doc += f"### Visual Notes\n{prompt.visual_notes}\n\n"
            doc += f"### Transition to Next Scene\n{prompt.transition}\n\n"
            doc += "---\n\n"

        return doc

    def to_script_document(self) -> str:
        """Generate the complete script document."""
        doc = f"# Campaign Script: {self.campaign_title}\n\n"
        doc += "---\n\n"

        for prompt in self.scene_prompts:
            doc += f"## Scene {prompt.scene_number}: {prompt.scene_title}\n\n"
            doc += f"{prompt.script}\n\n"
            doc += f"*[{prompt.transition.upper()} to next scene]*\n\n"
            doc += "---\n\n"

        doc += "## Full Script (Combined)\n\n"
        doc += self.full_script

        return doc
