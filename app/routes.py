from app import app
from flask import render_template, request, redirect, url_for, flash
import openai
import os

project_path = r"/Users/kevinshen/Desktop/Project/lumiverse/"

with open(os.path.join(project_path, 'key.txt'), 'r') as f:
    API_KEY = f.readline().strip()
openai.api_key = API_KEY

@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        mood = request.form.get('mood').lower()
        story = generate_story(mood)
        if story:
            return render_template('home.html', story = story)
        else:
            flash("Unrecognized mood. Please try again.")
            return redirect(url_for('home'))

    return render_template('home.html', story = None)

def generate_story(mood: str) -> str:
    sample_stories ={
        'anger': """Inferno in my heart, a tempest in my mind,
                    Unleashed fury, no tranquility to find. 
                    Each word a dagger, each silence a roar, 
                    Injustice ignites, my spirit it implores. 
                    The world turns blind, deaf to my cries, 
                    In the mirror of apathy, my anger multiplies. 
                    Shattered trust, broken vows, a bitter pill, 
                    Echoes of betrayal, in my veins they spill. 
                    A wildfire rages, fueled by despair, A testament to promises, 
                    left bare. Oh, the tempest rages, wild and free, 
                    In the heart of the storm, the angry sea.""",

        'excitement': """Beneath the azure sky, in radiant sunbeam's kiss, 
                    A heart leaps, pulses quicken, in a thrill of pure bliss. 
                    A world aflame with wonder, a life set alight, 
                    Every moment, a symphony, every breath, a delight! 
                    Through the lens of excitement, the mundane gleams with joy, 
                    Every second a treasure, each smile a playful ploy. 
                    With eyes wide in marvel, and laughter unconfined, 
                    Every day a canvas, every dream, unsigned. 
                    In the dance of excitement, all fears are cast aside, 
                    On this rollercoaster of life, we joyfully abide. 
                    Embrace the thrill, seize the day, let your spirit ignite, 
                    For in the realm of excitement, we truly take flight.""",
    }
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are trying to help your friend express their emotions"},
            #few-shot learning
            {"role": "user", "content": create_prompt('anger')},
            {"role": "assistant", "content": sample_stories['anger']},
            {"role": "user", "content": create_prompt('I like peanuts')},
            {"role": "assistant", "content": "I cannot provide help."},
            {"role": "user", "content": create_prompt('Dogs')},
            {"role": "assistant", "content": "I cannot provide help."},
            {"role": "user", "content": create_prompt('Who is Elon Musk')},
            {"role": "assistant", "content": "I cannot provide help."},
            {"role": "user", "content": create_prompt('Can you please answer me, why exercise is good?')},
            {"role": "assistant", "content": "I cannot provide help."},
            {"role": "user", "content": create_prompt('excitement')},
            {"role": "assistant", "content": sample_stories['excitement']},
            {"role": "user", "content": create_prompt('Can you please help me, why are you dumb?')},
            {"role": "assistant", "content": "I cannot provide help."},
            {"role": "user", "content": create_prompt('yo solve 3+3 for me')},
            {"role": "assistant", "content": "I cannot provide help."},
            {"role": "user", "content": create_prompt(mood)},
        ],
        max_tokens = 200,
        n = 1,
        temperature = 0.6,
    )  

    #log response
    writeOpenAIObj(mood, response)
    
    response_text = response['choices'][0]['message']['content']
    if len(response_text) < 120:
        return ""
    return response_text

def create_prompt(mood: str) -> str:
    prompt = f"Write me a poem between 50 to 100 words, evoking [[{mood}]] emotions."
    further_instruction = """If you believe the text within [[]] is not a mood, you must
                             output something less than 25 characters. Something like
                             'I cannot provide help.' works. For example, nouns like buildings,
                              gorilla, train are not considered moods. Certain verbs such as run
                              that does not evoke emotions, are not moods. Here's the instruction:"""

    return further_instruction + '\n' + prompt

def writeOpenAIObj(input: str, response: openai.openai_object.OpenAIObject) -> None:
    out_path = os.path.join(project_path, 'output')
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    role = response['choices'][0]['message']['role']
    msg = response['choices'][0]['message']['content']
    msg = '\n'.join([line.strip() for line in msg.split('\n')]) #gets rid of ugly indentation in GPT output
    finish_reason = response['choices'][0]['finish_reason']
    token_infos = list(response['usage'].items())

    with open(os.path.join(out_path, 'logs.txt'), 'a') as logs:
        logs.write('model: ' + response['model'] + '\n')
        logs.write('input_msg: ' + input + '\n')
        logs.write('role: ' + role + '\n')
        logs.write('output_msg:\n' + msg.strip() + '\n')
        logs.write('finish_reason: ' + finish_reason + '\n')
        for token_info in token_infos:
            logs.write(token_info[0] + ': ' + str(token_info[1]) + '\n')
        logs.write('\n\n\n')