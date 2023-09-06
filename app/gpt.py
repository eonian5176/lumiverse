import openai
import os

#GPT test file
openai.api_key = os.getenv("LUMIVERSE_OPENAI_API_KEY")
ppath = os.getenv("LUMIVERSE_PATH")
print(os.getenv("LUMIVERSE_OPENAI_API_KEY"))

# response = openai.ChatCompletion.create(
#     model='gpt-3.5-turbo',
#     messages=[
#         {"role": "user", "content": "test."},
#     ],
#     temperature=0,
#     max_tokens = 5,
# )

# model = response['model']
# role = response['choices'][0]['message']['role']
# msg = response['choices'][0]['message']['content']
# finish_reason = response['choices'][0]['finish_reason']
# print(model, role, msg, finish_reason, list(response['usage'].items()))