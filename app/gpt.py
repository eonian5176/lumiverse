import openai
openai.api_key = "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"


response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[
        {"role": "user", "content": "test."},
    ],
    temperature=0,
    max_tokens = 5,
)

model = response['model']
role = response['choices'][0]['message']['role']
msg = response['choices'][0]['message']['content']
finish_reason = response['choices'][0]['finish_reason']
print(model, role, msg, finish_reason, list(response['usage'].items()))