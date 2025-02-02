import re
import sys
import json
import random
import string
import pythainlp

import datetime as dt
from dateutil.relativedelta import relativedelta

from time import perf_counter

# check if python > 3.9
if sys.version_info[0:2] < (3, 9):
    raise AssertionError('This project requires Python 3.9 or higher.')

birthday = dt.datetime(2022, 1, 4)

resp_dir = [
    './responses/responses.json',
    './responses/responses_th.json',
    './responses/festivals.json',
    './responses/festivals_th.json',
    './responses/badwords.json',
    './responses/unknown_responses.json'
]

read_resp = []

for resp in resp_dir:
    with open(resp, 'r', encoding = 'utf-8') as read:
        read_resp.append(json.load(read))

(res_en, res_th, fes_en, fes_th, badwords, unknown_responses) = read_resp

res_data = res_en | res_th
fes_res_data = fes_en | fes_th

unknown_response_en = unknown_responses['en']   
unknown_response_th = unknown_responses['th']

def detect_thai(list_of_words: list[str]) -> bool:
    
    '''
        Determine of the list of string is Thai or not
    '''
    
    regexp = re.compile(rf'[{pythainlp.thai_characters}]')
    thai_prob = sum(1 for word in list_of_words if regexp.search(word))
    percentage = round((thai_prob / len(list_of_words)) * 100, 2)
    
    return percentage >= 50
    

def msg_probability(input_text: str, reconized_word: set[str], single_response: bool = False, required_words: set[str] = []) -> float:

    '''
        Calculate the probability of the sentence and return a word certainty percentage.
    '''

    has_required_word = True
    
    message_certainty = sum(1 for word in input_text if word in reconized_word)
    probability = message_certainty / len(reconized_word)
    
    for word in required_words:
        if word not in input_text:
            has_required_word = False
            break
        
    return probability * 100 if has_required_word or single_response else 0
    
    
def check_all_msg(message: list[str], is_thai: bool, date: dt.datetime) -> str:

    '''
        Check all the word in the tokenized string list and return the best response
    '''

    highest_prob_list = {}
    
    for e in message:
        if e in set(badwords['en']):
            return 'I\'m sorry you feel that way. I think you calm down just a little bit.'
        
        elif e in set(badwords['th']):
            return 'แบบนี้ไม่ดีเลยนะคะ เอาเป็นว่าคุณพี่ใจเย็นๆ แล้วค่อยมาคุยกันดีๆ ดีกว่านะคะ'
    
    def response(bot_response: str, list_of_words: set[str], single_response: bool = False, required_words: set[str] = []):
        nonlocal highest_prob_list
        highest_prob_list[bot_response] = msg_probability(message, list_of_words, single_response, required_words)
        

    for res in res_data:
        
        if not res_data[res]['list_of_words']:
            raise ValueError(f'Intents: "{res}" required a list of words to be functional.')
        
        response(
            random.choice(res_data[res]['response']), 
            list_of_words = set(res_data[res]['list_of_words']), 
            single_response = res_data[res]['is_single_response'], 
            required_words = set(res_data[res]['required_word'])
        )

    for fes_res in fes_res_data:
        
        if not fes_res_data[fes_res]['list_of_words']:
            raise ValueError(f'Intents: "{fes_res}" required a list of words to be functional.')
        
        if isinstance(fes_res_data[fes_res]['date'], int):
            date_frame = [dt.datetime(date.year, fes_res_data[fes_res]['month'], fes_res_data[fes_res]['date']).date()]
        
        elif isinstance(fes_res_data[fes_res]['date'], list):
            date_range = range(fes_res_data[fes_res]['date'][0], (fes_res_data[fes_res]['date'][1] + 1))
            date_frame =  [dt.datetime(date.year, fes_res_data[fes_res]['month'], d).date() for d in date_range]
        
        response(
            random.choice(fes_res_data[fes_res]['response']['fes' if date in date_frame else 'nonfes']),
            list_of_words = set(fes_res_data[fes_res]['list_of_words']), 
            single_response = fes_res_data[fes_res]['is_single_response'], 
            required_words = set(fes_res_data[fes_res]['required_word'])
        )
    
    unknown_response = unknown_response_th if is_thai else unknown_response_en
    
    best_match = max(highest_prob_list, key = highest_prob_list.get)
    
    return random.choice(unknown_response) if highest_prob_list[best_match] < 1 else best_match


def get_response(input_text: str, debug: bool = False) -> str:

    '''
        Parse string text input and find the best response for the sentence.
    '''

    start_timer = perf_counter()
    
    input_text = re.sub(r'[\^!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]', '', input_text)

    split_text = pythainlp.word_tokenize(input_text, keep_whitespace = False, engine = 'nercut')
    split_text = [e.lower() for e in split_text]
    
    if len(split_text) == 1:
        split_text = split_text[0].split()
    
    is_thai = detect_thai(split_text)

    response = check_all_msg(split_text, is_thai, dt.date.today())
    
    current_time = dt.datetime.now()
    age = relativedelta(current_time, birthday).years
    
    if re.finditer(r'(?<=(?<!\{)\{)[^{}]*(?=\}(?!\}))', response, re.MULTILINE) != set({}):
        response = string.Template(response).substitute(
            age = age,
            time = current_time.strftime('%H:%M:%S'),
            timezone = current_time.astimezone().tzinfo
        )
    
    end_timer = perf_counter()

    if debug:
        print(f'\u001b[42;1m -> \u001b[0m Incoming: {split_text}')
        print(f'\u001b[41;1m <- \u001b[0m Response with: {response}')
        print(f'\u001b[45;1m ** \u001b[0m Response time: {round((end_timer - start_timer) * 1000, 4)} ms')
        
    return response