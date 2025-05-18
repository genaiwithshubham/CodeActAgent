from dotenv import load_dotenv

load_dotenv()

from litellm import completion

model_name = "claude-3-5-sonnet-20240620"

messages = [{"role": "user", "content": "Hey! how's it going?"}]
response = completion(model=model_name, messages=messages)
print(response['choices'][0]['message']['content'])