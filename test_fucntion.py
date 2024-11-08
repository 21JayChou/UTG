
import os

from openai import OpenAI



# client = OpenAI(api_key=os.environ['OPENAI_KEY'])
client = OpenAI(api_key=test_api_key)
def chat_with_llm(prompt):
    try:
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text',
                         'text': prompt
                         }
                    ]
                }
            ],
            temperature=0.7
        )
        res = response.choices[0].message.content
        return res
    except Exception as e:
        print(f'Can not connect to llm:{e}')

res = chat_with_llm('hello')

print(res)
