"""Product and service information model for ad campaigns."""

from typing import Optional
from pydantic import BaseModel, Field


class ProductInfo(BaseModel):
    """Stores information about the product or service being advertised."""

    name: str = Field(
        description="Name of the product or service"
    )
    description: str = Field(
        description="Detailed description of what the product/service does"
    )
    target_audience: str = Field(
        description="Description of the target audience (demographics, interests, pain points)"
    )
    key_benefits: list[str] = Field(
        default_factory=list,
        description="List of key benefits and unique selling points"
    )
    emotional_tone: str = Field(
        default="inspiring",
        description="Desired emotional tone (inspiring, funny, urgent, heartwarming, bold, etc.)"
    )
    campaign_goal: str = Field(
        default="awareness",
        description="Primary campaign goal (awareness, conversion, engagement, brand building)"
    )
    ad_format: str = Field(
        default="video",
        description="Preferred ad format (video, carousel, single image, story)"
    )
    brand_colors: Optional[str] = Field(
        default=None,
        description="Brand colors to incorporate in visuals"
    )
    brand_voice: Optional[str] = Field(
        default=None,
        description="Brand voice characteristics (professional, casual, playful, etc.)"
    )
    competitors: Optional[str] = Field(
        default=None,
        description="Key competitors or market positioning context"
    )
    additional_notes: Optional[str] = Field(
        default=None,
        description="Any additional context or requirements"
    )

    def to_prompt_context(self) -> str:
        """Convert product info to a context string for prompts."""
        context = f"""
Product/Service: {self.name}
Description: {self.description}
Target Audience: {self.target_audience}
Key Benefits: {', '.join(self.key_benefits) if self.key_benefits else 'Not specified'}
Emotional Tone: {self.emotional_tone}
Campaign Goal: {self.campaign_goal}
Ad Format: {self.ad_format}
"""
        if self.brand_colors:
            context += f"Brand Colors: {self.brand_colors}\n"
        if self.brand_voice:
            context += f"Brand Voice: {self.brand_voice}\n"
        if self.competitors:
            context += f"Market Context: {self.competitors}\n"
        if self.additional_notes:
            context += f"Additional Notes: {self.additional_notes}\n"

        return context.strip()
