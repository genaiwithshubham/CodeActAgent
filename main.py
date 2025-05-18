from dotenv import load_dotenv

load_dotenv()

import chainlit as cl
from agents import CodeActAgent


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Solving a Simple Math Problem",
            message="Calculate the sum of all even numbers between 1 and 100.",
        ),
        cl.Starter(
            label="Data Analysis Task",
            message="Create a small dataset of 5 students with their names, ages, and test scores. Then calculate the average score and identify the student with the highest score. Finally, create a simple bar chart visualizing all students' scores.",
        ),
        cl.Starter(
            label="Algorithmic Challenge",
            message="Implement a function to check if a string is a palindrome. Then test it on these inputs: \"radar\", \"hello\", and \"A man, a plan, a canal: Panama\". The third test should ignore spaces, punctuation and case sensitivity.",
        ),
        cl.Starter(
            label="Solve a Complex Problem Step by Step",
            message="Implement the k-means clustering algorithm from scratch and demonstrate it on a simple 2D dataset. Generate some sample data with 3 clusters, visualize the data, apply k-means, and show the final clusters.",
        ),
    ]


# @cl.on_chat_start
# async def start_chat():
#     cl.user_session.set(
#         "message_history",
#         [{"role": "system", "content": "You are a helpful assistant."}],
#     )


@cl.on_message
async def main(message: cl.Message):

    # message_history = cl.user_session.get("message_history")
    # message_history.append({"role": "user", "content": message.content})

    agent = CodeActAgent(debug=False, max_cycles=3)
    solution = await agent.solve(message.content)

    # message_history.append({"role": "assistant", "content": solution})
    await cl.Message(
        content=solution,
    ).send()
