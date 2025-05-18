import chainlit as cl
from llms import call_litellm

@cl.step()
async def planner_tool(messages: list[dict[str, str]], cycle_number: int):
    
    current_step = cl.context.current_step
    current_step.input = {
        "message": messages[len(messages) - 1]["content"],
        cycle_number: cycle_number
    }
    
    complete_response = ""

    stream = call_litellm(model="ollama", messages=messages)
    
    for part in stream:
        if token := part.choices[0].delta.content or "":
            complete_response += token
            await current_step.stream_token(str(token))
    
    return complete_response