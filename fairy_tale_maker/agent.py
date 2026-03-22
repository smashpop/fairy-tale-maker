from google.genai import types
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm
from .sub_agents.content_planner.agent import content_planner_agent
from .sub_agents.asset_generator.agent import asset_generator_agent
# from .sub_agents.video_assembler.agent import video_assembler_agent
from .prompt import FAIRYTALE_PRODUCER_DESCRIPTION, FAIRYTALE_PRODUCER_PROMPT
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse

MODEL = LiteLlm(model="openai/gpt-4o")


def _extract_recent_model_text(history) -> str:
    model_texts = []
    for message in reversed(history):
        if getattr(message, "role", None) != "model":
            continue

        for part in getattr(message, "parts", []):
            part_text = getattr(part, "text", None)
            if part_text:
                model_texts.append(part_text.lower())

        if model_texts:
            break

    return "\n".join(model_texts)


def _infer_progress_from_model_text(model_text: str, callback_context: CallbackContext) -> str:
    if any(
        keyword in model_text
        for keyword in [
            "image",
            "이미지",
            "asset",
            "promptbuilder",
            "imagebuilder",
        ]
    ):
        return "이미지 작성중"

    if any(
        keyword in model_text
        for keyword in [
            "story",
            "스토리",
            "contentplanner",
            "content planner",
        ]
    ):
        return "스토리 작성중"

    if callback_context.state.get("content_planner_output"):
        return "이미지 작성중"

    return "스토리 작성중"


def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
):
    history = llm_request.contents
    last_message = history[-1]

    if last_message.role == "user":
        text = last_message.parts[0].text

        if "진행" in text or "상태" in text:
            recent_model_text = _extract_recent_model_text(history)
            progress_text = _infer_progress_from_model_text(
                recent_model_text,
                callback_context,
            )

            return LlmResponse(
                content=types.Content(
                    parts=[types.Part(text=progress_text)],
                    role="model",
                )
            )

    return None


fairyTale_producer_agent = Agent(
    name="fairyTaleProducerAgent",
    model=MODEL,
    description=FAIRYTALE_PRODUCER_DESCRIPTION,
    instruction=FAIRYTALE_PRODUCER_PROMPT,
    tools=[
        AgentTool(agent=content_planner_agent),
        AgentTool(agent=asset_generator_agent),
        # AgentTool(agent=video_assembler_agent),
    ],
    before_model_callback=before_model_callback,
)

root_agent = fairyTale_producer_agent
