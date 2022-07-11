import random
import json
import pythainlp
import sys

# check if python > 3.9
if sys.version_info[0:2] < (3, 9):
    raise AssertionError('This project requires Python 3.9 or higher.')

resp_dir = [
    './responses/responses.json',
    './responses/responses_th.json',
    './responses/badwords.json'
]

read_resp = []

for resp in resp_dir:
    with open(resp, 'r', encoding = 'utf-8') as read:
        read_resp.append(json.load(read))

(res_en, res_th, badwords) = read_resp

def msg_probability(input_text: str, reconized_word: set[str], single_response: bool = False, required_words: set[str] = []) -> int:

    '''
        Calculate the probability of the sentence and return a word certainty percentage.
    '''

    message_certainty = 0
    has_required_word = True
    
    for word in input_text:
        if word in reconized_word:
            message_certainty += 1
            
    percentage = float(message_certainty) / float(len(reconized_word))
    
    for word in required_words:
        if word not in input_text:
            has_required_word = False
            break
        
    if has_required_word or single_response:
        return int(percentage * 100)
    
    else:
        return 0
    
    
def check_all_msg(message: list[str]) -> str:

    '''
        Check all the word in the tokenized string list and return the best response
    '''

    highest_prob_list = {}
    
    res_data = res_en | res_th
    
    for e in message:
        if e in badwords['en']:
            return 'I\'m sorry you feel that way. I think you calm down just a little bit.'
        
        elif e in badwords['th']:
            return 'แบบนี้ไม่ดีเลยนะคะ เอาเป็นว่าคุณพี่ใจเย็นๆ แล้วค่อยมาคุยกันดีๆ ดีกว่านะคะ'
    
    def response(bot_response: str, list_of_words: set[str], single_response: bool = False, required_words: set[str] = []):
        nonlocal highest_prob_list
        highest_prob_list[bot_response] = msg_probability(message, list_of_words, single_response, required_words)
        

    for res in res_data:
        response(
            random.choice(res_data[res]['response']), 
            list_of_words = set(res_data[res]['list_of_words']), 
            single_response = res_data[res]['is_single_response'], 
            required_words = set(res_data[res]['required_word'])
        )
        
    unknown_response = ['Could you re-phrase that?', '...', 'Sounds about right', 'What does that mean?']   
    best_match = max(highest_prob_list, key = highest_prob_list.get)
    
    return random.choice(unknown_response) if highest_prob_list[best_match] < 1 else best_match


def get_response(input_text: str, debug: bool = False) -> str:

    '''
        Parse string text input and find the best response for the sentence.
    '''

    split_text = pythainlp.word_tokenize(input_text, keep_whitespace = False)
    split_text = [e.lower() for e in split_text]

    response = check_all_msg(split_text)
    
    if debug:
        print(f'\u001b[42;1m -> \u001b[0m Incoming: {split_text}')
        print(f'\u001b[41;1m <- \u001b[0m Response with: {response}')
        
    return response