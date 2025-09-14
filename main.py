import telebot
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

TG_TOKEN = os.getenv('TG_TOKEN')
OR_TOKEN = os.getenv('OR_TOKEN')

bot = telebot.TeleBot(TG_TOKEN)

client = OpenAI(
    base_url='https://openrouter.ai/api/v1',
    api_key=OR_TOKEN,
)

user_data = {}


@bot.message_handler(commands=['start', 'register'])
def sr(message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    bot.send_message(message.chat.id, 'entry your name: ')
    bot.register_next_step_handler(message, step_name)

def step_name(message):
    user_id = message.from_user.id 
    name = message.text.strip()
    
    if not name or not name.isalpha() or len(name) > 20:
        bot.send_message(message.chat.id, 'Wrong name! Try again:')
        bot.register_next_step_handler(message, step_name)
        return
    
    user_data[user_id]['name'] = name
    bot.send_message(message.chat.id, 'Good! how old are you:')
    bot.register_next_step_handler(message, step_age)

def step_age(message):
    user_id = message.from_user.id
    age = message.text.strip()

    if not age or not age.isdigit() or int(age) > 100 or int(age) < 0:
        bot.send_message(message.chat.id, 'Wrong age! Try again:')
        bot.register_next_step_handler(message, step_age)
        return
    
    user_data[user_id]['age'] = age
    bot.send_message(message.chat.id, 'Good! Now entry email address: ')
    bot.register_next_step_handler(message, step_email)

def step_email(message):
    user_id = message.from_user.id
    email = message.text.strip()

    if  '@' not in email or len(email) < 4:
        bot.send_message(message.chat.id, 'Wrong email! Try again')
        bot.register_next_step_handler(message, step_email) 
        return
    
    user_data[user_id]['email'] = email
    bot.send_message(message.chat.id, 'Good! Now entry your password:')
    bot.register_next_step_handler(message, step_password)

def step_password(message):
    user_id = message.from_user.id
    password = message.text.strip()

    x = [x for x in password if x.isalpha()]
    y = [x for x in password if x.isdigit()]

    if not x or not y or len(password) < 8:
        bot.send_message(message.chat.id, 'Wrong password! Try again')
        bot.register_next_step_handler(message, step_password) 
        return
    
    user_data[user_id]['password'] = password
    bot.send_message(message.chat.id, 'Good! Now tell us about yourself: list your hobbies, aspirations and fears. The description should include all three aspects. For example: I am fond of reading, I want to become a doctor, I am afraid of heights.: ')
    bot.register_next_step_handler(message, step_description)

def step_description(message):
    user_id = message.from_user.id
    description = message.text.strip()

    if not description:
        bot.send_message(message.chat.id, 'Description is not be empty! Try again')
        bot.register_next_step_handler(message, step_description) 
        return
    
    ai_response, is_valid = check_description(description)

    if is_valid:
        user_data[user_id]['description'] = description
        data = user_data[user_id]
        mes = 'Registrtion complete!'
        for key in data:
            mes += f"\n{key} - {data[key]}"
            
        bot.send_message(message.chat.id, mes)
        del user_data[user_id]
    else:
        bot.send_message(message.chat.id, f"The description failed verification. AI responded: '{ai_response}'. Make sure you have specified your hobbies, aspirations and fears. Try re-entering. For example: 'I am fond of reading, I aspire to be a doctor, and I am afraid of heights.'")
        bot.register_next_step_handler(message, step_description)

def check_description(description):
    prompt =(
        f"Check if the following description explicitly includes three aspects: hobbies (увлечения), aspirations (стремления), and fears (страхи). "
        f"Consider synonyms like 'I like', 'I enjoy', 'I want to', 'I aim to', 'I am afraid of', etc. "
        f"Respond only with 'yes' or 'no'. Description: {description}"
    ) 
    try:
        response = client.chat.completions.create(
            model='deepseek/deepseek-r1-0528:free',
            messages=[
                {'role': 'system', 'content': "You are a strict checker. Respond only 'yes' or 'no'."},
                {'role': 'user', 'content': prompt} 
            ],
            timeout=10
        )
        ai_response = response.choices[0].message.content.strip().lower()
        print(f"{description}, --- {ai_response}")
        return ai_response, ai_response == 'yes'
    
    except Exception as e:
        print(f"ERROR - {e}")
        return f"ERROR - {e}", False


@bot.message_handler(func=lambda message: True)
def ai_generated(message):
    user_text = message.text.strip()
    if not user_text:
        bot.send_message(message.chat.id, 'entry text or start registration')
        return
    
    response = client.chat.completions.create(
        model='deepseek/deepseek-r1-0528:free',
        messages=[
            {'role': 'system', 'content': '"I briefly helped the user, and then I remembered about the need to register in my bot using the /register command" '},
            {'role': 'user', 'content': f'user text: {user_text}'}  
        ],
        extra_headers= {
            "HTTP-Referer": "http://localhost:8080/",
            "X-title": "my bot"
    } 

    )

    bot.send_message(message.chat.id, f'{response.choices[0].message.content}')



print(1)
bot.polling()
