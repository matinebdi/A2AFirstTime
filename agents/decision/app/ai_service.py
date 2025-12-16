"""AI Service - Google Gemini Integration"""

import logging
from typing import Optional

import google.generativeai as genai

from .config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered decision making using Google Gemini"""

    def __init__(self):
        self.model: Optional[genai.GenerativeModel] = None
        self.enabled = False

    def initialize(self):
        """Initialize Gemini AI"""
        if not settings.google_api_key:
            logger.warning("⚠️  No Google API Key provided. AI features disabled.")
            return

        try:
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
            self.enabled = True
            logger.info("✅ Google Gemini AI initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini AI: {e}")
            self.enabled = False

    async def analyze_task(self, task: str, context: dict) -> dict:
        """
        Analyze a task and create an action plan using AI

        Args:
            task: The user task to analyze
            context: Additional context about the task

        Returns:
            Dictionary with decision, actions, and reasoning
        """
        if not self.enabled or not self.model:
            return {
                "decision": "ai_unavailable",
                "actions": [],
                "reasoning": "AI service is not available",
            }

        try:
            prompt = f"""
You are a Decision Agent in a multi-agent UI automation system.

**Your role**: Analyze user tasks and create detailed action plans.

**User Task**: {task}

**Context**: {context}

**Available Agents**:
- vision: Analyzes UI elements (screenshots, buttons, forms)
- form: Fills form fields with data
- validation: Verifies action success

**Instructions**:
1. Break down the task into specific actions
2. Determine which agents to invoke
3. Specify the sequence of operations
4. Provide clear reasoning

**Output Format** (JSON):
{{
  "decision": "proceed|wait|reject",
  "actions": [
    {{"agent": "vision", "action": "analyze_ui", "params": {{}}}},
    {{"agent": "form", "action": "fill_field", "params": {{"field": "username", "value": "test"}}}}
  ],
  "reasoning": "Explanation of the decision",
  "estimated_steps": 3
}}

Respond ONLY with valid JSON. No markdown, no explanation outside JSON.
"""

            response = await self.model.generate_content_async(prompt)
            result_text = response.text.strip()

            # Remove markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()

            # Parse JSON
            import json
            result = json.loads(result_text)

            logger.info(f"AI Decision: {result.get('decision', 'unknown')}")
            return result

        except Exception as e:
            logger.error(f"Error in AI analysis: {e}", exc_info=True)
            return {
                "decision": "error",
                "actions": [],
                "reasoning": f"AI analysis failed: {str(e)}",
            }

    async def evaluate_context(self, context: dict) -> str:
        """
        Evaluate current context and provide insights

        Args:
            context: Current state/context to evaluate

        Returns:
            String with evaluation results
        """
        if not self.enabled or not self.model:
            return "AI service unavailable"

        try:
            prompt = f"""
Analyze the following context and provide insights:

{context}

Provide a brief analysis (2-3 sentences) of what's happening and any recommendations.
"""

            response = await self.model.generate_content_async(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error in context evaluation: {e}")
            return f"Evaluation failed: {str(e)}"


# Global AI service instance
ai_service = AIService()
