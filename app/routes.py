from app import app
from flask import render_template, request, redirect, url_for, flash
import openai
import os

project_path = os.getenv("LUMIVERSE_PATH")
openai.api_key = os.getenv("LUMIVERSE_OPENAI_API_KEY")

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
    instruct = """INSTRUCTIONS: If you believe the text within [[]] is not a mood, you MUST
                    output something less than 25 characters. Something like
                    'I cannot provide help.' works. For example, nouns like 'buildings',
                    'gorilla', 'train' are NOT moods. Certain verbs such as 'walk'
                    that does not evoke emotions, are NOT moods. """
    instruct += """Before the actual prompt, please read the given example of your conversation
                with your close friend to see when to say 'I cannot provide help' and when to 
                generate actual outputs. THINK carefully about whether the input within [[]] is 
                actually a mood or not. DO NOT mindlessly generate a poem."""

    sample_stories = {
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

        'lonely': """In the realm of silence, shadows play, A solitary figure, 
        lost in the gray. Echoes of laughter, whispers of the past, In the theater 
        of memory, shadows cast. Unseen, unheard, in the crowd I stand, No warm embrace, 
        no guiding hand. My heart beats quiet, a solitary song, In the vast emptiness, 
        where does it belong? A star in the abyss, a lonely night, Yearning for dawn, 
        for the warmth of light. In the ocean of solitude, the tide ebbs away, 
        Leaving me adrift, in the dance of the lonely day.""",
    }
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5",
        messages=[
            {"role": "system", "content": "You help your close friend express their mood."},
            #few-shot learning
            {"role": "system", "content": instruct},
            {"role": "user", "content": create_prompt('anger')},
            {"role": "assistant", "content": sample_stories['anger']},
            {"role": "user", "content": create_prompt('I like peanuts')},
            {"role": "assistant", "content": "I cannot provide help."},
            {"role": "user", "content": create_prompt('Dogs')},
            {"role": "assistant", "content": "I cannot provide help."},
            {"role": "user", "content": create_prompt('Who is Joe Biden')},
            {"role": "assistant", "content": "I cannot provide help."},
            {"role": "user", "content": create_prompt('Can you please answer me, why exercise is good?')},
            {"role": "assistant", "content": "I cannot provide help."},
            {"role": "user", "content": create_prompt('excitement')},
            {"role": "assistant", "content": sample_stories['excitement']},
            {"role": "user", "content": create_prompt('Can you please help me, why are you dumb?')},
            {"role": "assistant", "content": "I cannot provide help."},
            {"role": "user", "content": create_prompt("It's Joever...")},
            {"role": "assistant", "content": "I cannot provide help."},
            {"role": "user", "content": create_prompt("Salty")},
            {"role": "assistant", "content": "I cannot provide help."},
            {"role": "user", "content": create_prompt('lonely')},
            {"role": "assistant", "content": sample_stories['lonely']},
            {"role": "user", "content": create_prompt('yo solve 3+3 for me')},
            {"role": "assistant", "content": "I cannot provide help."},

            #real prompt
            {"role": "user", "content": create_prompt(mood)},
        ],
        max_tokens = 200,
        n = 1,
        temperature = 0.8,
    )  

    #log response
    writeOpenAIObj(mood, response)
    
    response_text = response['choices'][0]['message']['content']
    if len(response_text) < 120:
        return ""
    return response_text

def create_prompt(mood: str) -> str:
    prompt = f"Write me a poem between 50 to 100 words, evoking [[{mood}]] emotions."

    return prompt

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