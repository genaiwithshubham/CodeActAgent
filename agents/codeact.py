import os
import sys
import subprocess
import traceback
from typing import Dict, List, Any, Tuple
import uuid

from tools import planner_tool


class CodeActAgent:
    """
    CodeAct Agent: A framework that implements the thought-execute-observe pattern
    for solving problems using LLMs with executable Python code.
    """

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20240620",
        max_cycles: int = 3,
        debug: bool = False,
    ):
        """
        Initialize the CodeAct agent.

        Args:
            model: Model identifier to use
            api_base: Base URL for API requests
            max_cycles: Maximum number of thought-execute-observe cycles
            debug: Whether to print debug information
        """
        self.model = model
        self.max_cycles = max_cycles
        self.debug = debug
        self.conversation_history = []
        self.execution_count = 0

    def _construct_system_prompt(self) -> str:
        """Create the system prompt that guides the agent's behavior."""

        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        file_path = os.path.join(project_dir, "prompts", "codeact_system_prompt.txt")
        with open(file_path, "r", encoding="utf-8") as file:
            prompt_template = file.read()
        return prompt_template

    def _execute_code(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code safely and return the results.

        Args:
            code: Python code to execute

        Returns:
            Dictionary containing execution results or error information
        """
        # Create a temporary file to write the code
        self.execution_count += 1
        temp_file = f"temp_execution_{self.execution_count}_{uuid.uuid4().hex}.py"

        try:
            with open(temp_file, "w") as f:
                f.write(code)

            # Execute the code in a separate process
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Code execution timed out after 30 seconds",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def _extract_code_blocks(self, text: str) -> List[str]:
        """
        Extract code blocks marked with <execute> tags from text.

        Args:
            text: Text containing code blocks

        Returns:
            List of extracted code blocks
        """
        code_blocks = []
        current_pos = 0

        while True:
            start_tag = text.find("<execute>", current_pos)
            if start_tag == -1:
                break

            end_tag = text.find("</execute>", start_tag)
            if end_tag == -1:
                break

            # Extract the code and strip any leading/trailing whitespace
            code = text[start_tag + len("<execute>") : end_tag].strip()
            code_blocks.append(code)

            current_pos = end_tag + len("</execute>")

        return code_blocks

    async def _process_cycle(
        self, user_query: str, cycle_number: int
    ) -> Tuple[str, bool]:
        """
        Process a single thought-execute-observe cycle.

        Args:
            user_query: The original user query
            cycle_number: Current cycle number

        Returns:
            Tuple of (agent_response, is_complete)
        """
        # Build messages for LLM
        messages = [
            {"role": "system", "content": self._construct_system_prompt()},
            {"role": "user", "content": user_query},
        ]

        # Add previous conversation history
        for msg in self.conversation_history:
            messages.append(msg)

        # Call the LLM to get the current cycle response
        if self.debug:
            print(f"\n--- Cycle {cycle_number} ---")
            print("Calling LLM API...")

        llm_response = await planner_tool(messages=messages, cycle_number=cycle_number)

        if self.debug:
            print(f"LLM Response: {llm_response[:100]}...")

        # Extract all code blocks from the response
        code_blocks = self._extract_code_blocks(llm_response)

        # Process and execute each code block
        execution_results = []
        for i, code in enumerate(code_blocks):
            if self.debug:
                print(f"\nExecuting code block {i+1}:")
                print(code[:100] + "..." if len(code) > 100 else code)

            result = self._execute_code(code)
            execution_results.append(result)

            if self.debug:
                if result["success"]:
                    print(f"Execution successful. Output: {result['stdout'][:100]}...")
                else:
                    print(
                        f"Execution failed: {result.get('error', result.get('stderr', 'Unknown error'))}"
                    )

        # Replace <execute> blocks with both code and execution results
        modified_response = llm_response
        for i, (code, result) in enumerate(zip(code_blocks, execution_results)):
            # Find the positions of the current execute block
            start_tag = modified_response.find("<execute>")
            end_tag = modified_response.find("</execute>", start_tag) + len(
                "</execute>"
            )

            # Create a new block with the code and execution results
            execution_block = f"<execute>\n{code}\n</execute>\n"

            if result["success"]:
                execution_block += f"<execution_result>\nExecution successful. Output:\n{result['stdout']}</execution_result>\n"
            else:
                error_msg = result.get("error", result.get("stderr", "Unknown error"))
                execution_block += f"<execution_result>\nExecution failed with error:\n{error_msg}</execution_result>\n"

            # Replace the original block with the new one
            modified_response = (
                modified_response[:start_tag]
                + execution_block
                + modified_response[end_tag:]
            )

        # Update conversation history
        self.conversation_history.append(
            {"role": "assistant", "content": modified_response}
        )

        # Determine if we should continue with another cycle or not
        # Check if the response indicates a final answer
        is_complete = (
            "final answer" in modified_response.lower()
            or "conclusion" in modified_response.lower()
            or cycle_number >= self.max_cycles
        )

        if not is_complete and cycle_number < self.max_cycles:
            # Add a transition message for the next cycle
            self.conversation_history.append(
                {
                    "role": "user",
                    "content": "Continue with the next cycle of thought-execute-observe to make further progress.",
                }
            )

        return modified_response, is_complete

    async def solve(self, user_query: str) -> str:
        """
        Solve the user's query using the thought-execute-observe pattern.

        Args:
            user_query: The user's question or problem

        Returns:
            The agent's final response with the solution
        """
        self.conversation_history = []
        current_cycle = 1
        complete = False
        final_response = ""

        while not complete and current_cycle <= self.max_cycles:
            cycle_response, complete = await self._process_cycle(
                user_query, current_cycle
            )
            final_response = cycle_response
            current_cycle += 1

            if self.debug:
                print(f"\nCycle {current_cycle-1} complete. Final: {complete}")

        # Clean up the final response for presentation
        cleaned_response = self._clean_response_for_output(final_response)

        return cleaned_response

    def _clean_response_for_output(self, response: str) -> str:
        """
        Clean up the final response for presentation to the user.

        Args:
            response: Raw response with tags

        Returns:
            Cleaned response suitable for user presentation
        """
        # This method can be expanded to format the response in a more readable way
        # For now, we'll keep it simple and just return the raw response
        return response
