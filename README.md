# CodeAct Agent

A Python implementation of thought-execute-observe pattern(CodeAct) for problem-solving using large language models with executable Python code.

## Overview

[CodeAct](https://arxiv.org/abs/2402.01030) is an agent framework that enables large language models (LLMs) to solve complex problems by combining structured reasoning with Python code execution. The agent follows a three-step cycle:

1. **Think**: The agent reasons about the problem and formulates an approach
2. **Execute**: The agent writes and runs Python code to implement its approach
3. **Observe**: The agent analyzes the execution results and decides on next steps

This cycle repeats until the problem is solved or a maximum number of iterations is reached.

## Features

- 🧠 **Structured Reasoning**: Clear thought-execute-observe pattern for step-by-step problem solving
- 🔒 **Safe Code Execution**: Isolated execution environment with timeout protection
- 📊 **Wide Range of Applications**: Suitable for data analysis, algorithm development, scientific computing, and more
- 🔄 **Iterative Refinement**: Multiple thought cycles allow for debugging and improvement
- 📝 **Detailed Documentation**: Includes code comments, examples, and prompt engineering guide


## Quick Start

```python
from codeact_agent import CodeActAgent
import os

# Initialize the agent
agent = CodeActAgent(
    model="claude-3-7-sonnet-20250219"
)

# Solve a problem
query = "Calculate the sum of all even numbers between 1 and 100."
solution = agent.solve(query)
print(solution)
```

## Configuration Options

The `CodeActAgent` constructor accepts the following parameters:

| Parameter   | Type   | Default                       | Description                              |
|-------------|--------|-------------------------------|------------------------------------------|
| `model`     | str    | "claude-3-7-sonnet-20250219"  | Model identifier to use                  |
| `max_cycles`| int    | 5                             | Maximum thought-execute-observe cycles   |
| `debug`     | bool   | False                         | Whether to print debug information       |

## Example Use Cases

The CodeAct agent can solve a wide variety of problems, including:

### Data Analysis

```python
query = """
Create a small dataset of 5 students with their names, ages, and test scores.
Then calculate the average score and identify the student with the highest score.
Finally, create a simple bar chart visualizing all students' scores.
"""
```

### Algorithm Implementation

```python
query = """
Implement a function to check if a string is a palindrome. 
Then test it on these inputs: "radar", "hello", and "A man, a plan, a canal: Panama".
The third test should ignore spaces, punctuation and case sensitivity.
"""
```

### Scientific Computing

```python
query = """
Implement the k-means clustering algorithm from scratch and demonstrate it on a simple 2D dataset.
Generate some sample data with 3 clusters, visualize the data, apply k-means, and show the final clusters.
"""
```

## Project Structure

- `codeact_agent.py`: Main implementation of the CodeAct agent
- `examples.md`: Usage examples showing the agent in action
- `prompt_engineering_guide.md`: Guide for customizing prompts for different use cases

## Customizing the Agent

The agent's behavior can be customized by:

1. Modifying the system prompt in the `_construct_system_prompt()` method
2. Adjusting the maximum number of cycles with the `max_cycles` parameter
3. Changing the model with the `model` parameter

See the `prompt_engineering_guide.md` file for detailed guidance on customizing the agent's prompts.

## Safety Considerations

The CodeAct agent executes Python code, which can potentially perform system operations. The implementation includes several safety features:

- Code execution in isolated processes
- Execution timeouts (default: 30 seconds)
- Temporary file cleanup

However, be cautious when using the agent with untrusted inputs or in production environments.

## Requirements

- Python 3.10+
- `litellm` package

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

This project was inspired by:
- ReAct (Reasoning + Acting) pattern
- Chain-of-thought prompting techniques
- Code as a form of reasoning in AI systems

---

For more information, check out the examples and prompt engineering guide included in the project.
