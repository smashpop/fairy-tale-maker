from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import CONTENT_PLANNER_DESCRIPTION, CONTENT_PLANNER_PROMPT
from pydantic import BaseModel, Field
from typing import List


class SceneOutput(BaseModel):
    id: int = Field(description="Page ID number")
    story_text: str = Field(description="Narrative text for the page")
    visual_description: str = Field(
        description="Illustration description for the page"
    )
    text_overlay: str = Field(
        description="Short optional text overlay for the image"
    )
    text_overlay_location: str = Field(
        description="Where to position the text on the image (e.g., 'top', 'bottom', 'center')"
    )


class ContentPlanOutput(BaseModel):
    title: str = Field(description="The fairy tale title")
    pages: List[SceneOutput] = Field(
        description="List of story pages in reading order"
    )


MODEL = LiteLlm(model="openai/gpt-4o")

content_planner_agent = Agent(
    name="ContentPlannerAgent",
    description=CONTENT_PLANNER_DESCRIPTION,
    instruction=CONTENT_PLANNER_PROMPT,
    model=MODEL,
    output_schema=ContentPlanOutput,
    output_key="content_planner_output",
)
