from litellm import completion


def call_litellm(model: str, messages: list[dict[str, str]]) -> str:
    """
    Call the LLM with the given messages.

    Args:
        messages: List of message dictionaries

    Returns:
        The model's response text
    """

    model_list = [
        {
            "model_name": "claude",
            "litellm_params": {"model": "claude-3-5-sonnet-20240620"},
        },
        {
            "model_name": "ollama",
            "litellm_params": {
                "model": "ollama_chat/llama3.2",
                "api_base": "http://localhost:11434",
            },
        },
    ]

    response = completion(model=model, messages=messages, model_list=model_list, stream=True)
    # return response["choices"][0]["message"]["content"]
    return response
