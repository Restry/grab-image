

# Note: The openai-python library support for Azure OpenAI is in preview.
import os
import openai
openai.api_type = "azure"
openai.api_base = "https://resley-openai.openai.azure.com/"
openai.api_version = "2022-12-01"
# os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

# defining a function to create the prompt from the system message and the messages


def create_prompt(system_message, messages):
    prompt = system_message
    message_template = "\n<|im_start|>{}\n{}\n<|im_end|>"
    for message in messages:
        prompt += message_template.format(message['sender'], message['text'])
    prompt += "\n<|im_start|>assistant\n"
    return prompt


# defining the system message
system_message_template = "<|im_start|>system\n{}\n<|im_end|>"
system_message = system_message_template.format(
    "You are an AI assistant that helps people find information.")

# creating a list of messages to track the conversation
messages = [{"sender": "user", "text": "如何在azure订阅中添加外部账号并赋予权限"}]
response = openai.Completion.create(
    engine="gpt35",
    prompt=create_prompt(system_message, messages),
    temperature=0.5,
    max_tokens=2200,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=["<|im_end|>"])


text = response['choices'][0]['text'].replace(
    '\n', '').replace(' .', '.').strip()
print(text)
