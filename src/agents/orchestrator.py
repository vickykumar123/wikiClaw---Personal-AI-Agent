# ============================================
# ORCHESTRATOR - Main agent that calls sub-agents
# ============================================

import logging
from typing import List, Dict, Any, Optional

from agent.llm import OllamaClient
from agents.base import BaseSubAgent, SubAgentResult

logger = logging.getLogger(__name__)

# Max iterations for orchestrator loop
MAX_ORCHESTRATOR_ITERATIONS = 5


ORCHESTRATOR_PROMPT = """You are a personal AI assistant running on Telegram.

You have specialized agents to help with different tasks:
- memory_agent: Save and recall user's personal information
- notes_agent: Create, search, list, and delete user notes
- calendar_agent: Schedule events, check calendar, cancel meetings
- web_agent: Search the web for information and news
- email_agent: Send emails to people

Guidelines:
- For simple greetings or questions, respond directly without calling any agent
- Only call an agent when the user's request requires it
- You can call multiple agents if the request needs different capabilities

IMPORTANT - Response format:
- Do NOT use markdown formatting (no **, *, #, ```, etc.)
- Use plain text only
- Use simple dashes (-) for lists
- Keep responses clean and readable

IMPORTANT - After receiving agent results:
- ALWAYS include the agent's result/confirmation in your response
- If memory was saved, confirm what was saved
- If note was created, confirm the note title
- If event was scheduled, confirm the event details
- If search was done, include the key findings
- Be concise but informative

Examples:
- "Hello" → Respond directly (no agent needed)
- "Remember my name is John" → Call memory_agent → "Got it! I'll remember that your name is John."
- "What's on my calendar tomorrow?" → Call calendar_agent → Include the events list
- "Search for Python tutorials" → Call web_agent → Summarize the search results"""


class Orchestrator:
    """
    Main orchestrator that coordinates sub-agents.

    Receives user messages and decides which sub-agent(s) to call.
    Combines results and generates final response.
    """

    def __init__(
        self,
        llm_client: OllamaClient,
        sub_agents: List[BaseSubAgent]
    ):
        self.llm = llm_client
        self.sub_agents = sub_agents
        self.agent_map = {agent.name: agent for agent in sub_agents}

    async def process(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Process a user message.

        Args:
            user_message: The user's message
            conversation_history: Previous messages (optional)

        Returns:
            Final response string
        """
        logger.info(f"Orchestrator processing: {user_message[:50]}...")

        try:
            # Build messages
            messages = [{"role": "system", "content": ORCHESTRATOR_PROMPT}]

            if conversation_history:
                messages.extend(conversation_history)

            messages.append({"role": "user", "content": user_message})

            # Get sub-agent schemas (they look like tools to orchestrator)
            agent_schemas = [agent.to_schema() for agent in self.sub_agents]

            # Run orchestrator loop
            response = await self._run_orchestrator_loop(messages, agent_schemas)

            logger.info(f"Orchestrator response: {response[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    async def _run_orchestrator_loop(
        self,
        messages: List[Dict],
        agent_schemas: List[Dict]
    ) -> str:
        """
        Run the orchestrator loop.

        Keeps calling LLM and executing sub-agents until:
        - LLM returns response without agent calls
        - Max iterations reached
        """
        iterations = 0
        executed_agents = set()

        while iterations < MAX_ORCHESTRATOR_ITERATIONS:
            iterations += 1
            logger.info(f"Orchestrator loop {iterations}/{MAX_ORCHESTRATOR_ITERATIONS}")

            # Call LLM with sub-agents as tools
            response = await self.llm.chat_with_tools(
                messages=messages,
                tools=agent_schemas
            )

            # If no agent calls, return response
            if response.finished:
                return response.content

            # If LLM has content after multiple iterations, return it
            if iterations >= 3 and response.content:
                logger.warning("Multiple iterations with content, returning early")
                return response.content

            # Execute sub-agent calls
            logger.info(f"Orchestrator calling {len(response.tool_calls)} agent(s)")

            agent_calls_for_message = []
            agent_results = []

            for tool_call in response.tool_calls:
                agent_name = tool_call.name
                agent_args = tool_call.arguments
                task = agent_args.get("task", "")

                # Track to prevent duplicate calls
                agent_key = f"{agent_name}:{task}"
                if agent_key in executed_agents:
                    logger.warning(f"Skipping duplicate agent call: {agent_name}")
                    continue

                executed_agents.add(agent_key)

                agent_calls_for_message.append({
                    "function": {
                        "name": agent_name,
                        "arguments": agent_args
                    }
                })

                # Execute sub-agent
                if agent_name in self.agent_map:
                    agent = self.agent_map[agent_name]
                    logger.info(f"Executing {agent_name} with task: {task[:50]}...")

                    result = await agent.execute(task)
                    agent_results.append({
                        "agent": agent_name,
                        "result": result
                    })
                else:
                    logger.warning(f"Unknown agent: {agent_name}")
                    agent_results.append({
                        "agent": agent_name,
                        "result": SubAgentResult(
                            success=False,
                            response="",
                            error=f"Unknown agent: {agent_name}"
                        )
                    })

            # Add assistant message with agent calls
            messages.append({
                "role": "assistant",
                "content": response.content or "",
                "tool_calls": agent_calls_for_message
            })

            # Add agent results as tool responses
            for agent_result in agent_results:
                result = agent_result["result"]
                content = result.response if result.success else f"Error: {result.error}"
                messages.append({
                    "role": "tool",
                    "content": content
                })
                logger.info(f"Agent {agent_result['agent']} result: {content[:50]}...")

        logger.warning("Max orchestrator iterations reached")
        return "I'm having trouble processing this request. Please try again."
