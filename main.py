from parse_recipe import get_recipe, num
import nltk
import json
import re
import string

'''
Requirements:
1. Recipe retrieval and display (see example above, including "Show me the ingredients list");
2. Navigation utterances ("Go back one step", "Go to the next step", "Take me to the 1st step", "Take me to the n-th step");
3. Vague "how to" questions ("How do I do that?", in which case you can infer a context based on what's parsed for the current step);
4. Specific "how to" questions ("How do I <specific technique>?");
.5 Name your bot :)
'''

recipe = None
curr_step = 0
curr_step_hows = None
num_steps = 0
with open('methods.json') as f:
    METHODS = json.load(f)["METHODS"]


def run():
    ip = input('Hi, I\'m RecipeBot9000! Please provide the URL to the recipe you want some help with! Type \'exit\' to quit.\n\n> ')
    while True:
        ip = parse_input(ip)
        # print(f'ip: {ip}')
        if ip == 'exit':
            break


def parse_input(ip):
    # print(f'parse_input ip: {ip}')
    global recipe
    global curr_step
    global num_steps
    global curr_step_hows

    worded_steps = {'first': 1, 'second': 2, 'third': 3, 'fourth': 4,
                    'fifth': 5, 'sixth': 6, 'seventh': 7, 'eight': 8, 'ninth': 9, 'tenth': 10}

    if type(ip) is not tuple and 'www.allrecipes.com/recipe/' in ip:
        recipe = get_recipe(ip)
        print(f'\n\n{recipe["name"]}? Sounds tasty! What do you want to do?')
        num_steps = len(recipe['directions'])
        curr_step = 0
        curr_step_hows = None
        # print(f'Num step: {num_steps}')
        ip = input(
            '[1] Go over ingredients list or [2] Go over recipe steps.\n\n> ')
        return ip
    elif type(ip) is not tuple and ip.lower() == 'exit':
        return 'exit'
    elif not recipe:
        ip = input('\n\nPlease enter a recipe URL first.\n\n> ')
        return ip
    elif type(ip) is tuple and ip[0] == 'answer_how_to_vague' and ip[1] not in list(str(curr_step_hows.keys()))+[0]:
        # print('me!!')
        return ip[1]
    elif type(ip) is tuple and ip[0] == 'answer_how_to_vague' and ip[1] == 0:
        s = ''
        # print(f'curr_step_hows: {curr_step_hows}')
        for key, val in curr_step_hows.items():
            s += f'[{key}]: {val} '
        if len(list(curr_step_hows.keys())) == 1:
            return ('answer_how_to_vague', '1')
        elif len(list(curr_step_hows.keys())) > 1:
            ip = input(f'\n\nWhich part? '+s+'\nIf none of these are what you want, try asking a specific question.\n\n> ')
            return ('answer_how_to_vague', ip)
        else: 
            ip = input('\n\nI don\'t detect any how-tos here. Try asking a specific how-to.\n\n> ')
            return ip
    elif type(ip) is tuple and ip[0] == 'answer_how_to_vague' and ip[1] != 0:
        ans = curr_step_hows[int(ip[1])]
        print(
            f'\n\nTry this: https://www.google.com/search?q=how+to+{re.sub(" ","+",ans)}\n\n')
        ip = input('> ')
        return ip
    elif type(ip) is tuple and ip[0] == 'answer_how_to_specific':
        print(
            f'\n\nTry this: https://www.google.com/search?q=how+to+{re.sub(" ","+",ip[1].strip(" ?"))}\n\n')
        ip = input('> ')
        return ip
    elif re.search(r'(?i)\bhow\b', ip.lower()):
        # print(f'asked how: {ip}')
        op = parse_how_to(ip)
        return op
    elif ip == '1' or any(i in ip.lower() for i in ['ingredients', 'ingredient']):
        print(f'\n\nHere is the ingredients list for {recipe["name"]}:')
        for ing in recipe['ingredients']:
            print(f'\t- {ing}')
        ip = input('\n\n> ')
        return ip
    elif ip == '2' or any(i in ip.lower() for i in ['direction', 'directions']):
        if curr_step < num_steps:
            # curr_step += 1
            print(
                f'\n\nStep {curr_step+1} is: {recipe["directions"][curr_step]}\n\n')
            ip = input('> ')
            return ip
        else:
            return 'step out of range'
    elif any(num(x) for x in re.sub(r'(?i)st|rd|th|nd', '', ip).split()) and 'step' in ip.lower():
        cs = int(
            num(next(x for x in re.sub(r'(?i)st|rd|th|nd', '', ip).split() if num(x))))
        if cs > 0 and cs <= num_steps:
            curr_step = cs - 1
            # print(f'curr_step: {curr_step}')
            return '2'
        else:
            return 'step out of range'
    elif (any(x for x in worded_steps.keys() if x in ip)) and 'step' in ip.lower():
        cs = worded_steps[[x for x in worded_steps.keys() if x in ip][0]]
        if cs > 0 and cs <= num_steps:
            curr_step = cs - 1
            # print(f'curr_step: {curr_step}')
            return '2'
        else:
            return 'step out of range'

    elif 'next' in ip.lower() and 'step' in ip.lower():
        if curr_step < num_steps - 1:
            curr_step += 1
            return '2'
        else:
            return 'step out of range'
    elif ('previous' in ip.lower() or 'last' in ip.lower() or 'back' in ip.lower()) and 'step' in ip.lower():
        if curr_step > 0:
            curr_step -= 1
            return '2'
        else:
            return 'step out of range'
    elif ip == 'step out of range':
        ip = input('\n\nThat step doesn\'t exist. Try something else.\n\n> ')
        return ip
    else:
        ip = input('\n\nI don\'t understand. Try something else.\n\n> ')
        return ip


def parse_how_to(ip):
    # print(f'PARSE ip: {ip}')
    # vague if:
    #   - no VB/VBP (eg, How?)
    #   - all VB/VBPs are 'do' (eg, How do I do that?)
    tokens = nltk.pos_tag(nltk.word_tokenize(ip.lower()))
    t = [i for i, x in enumerate(tokens) if x[1] in ['VB', 'VBP']]
    if not t or all(tokens[i][0] in ['do', 'i'] for i in t):
        # print(f'VAGUE')
        return vague_how_to(ip)
    else:
        # print('SPECIFIC')
        return specific_how_to(ip)


def vague_how_to(ip):
    global METHODS
    global curr_step_hows
    # super hacky lol
    imperatives = [
        x+'. ' for x in re.split('[.;]|(?='+')|(?='.join(METHODS)+')', recipe['directions'][curr_step].lower())]
    print(f'imperatives: {imperatives}')
    possible = [sub[0].strip(',') for sub in
                [[x[x.find(t):x.find(next((x for x in x[x.find(t)+len(t):].split() if x in METHODS), '###'))]
                  for t in x.split()
                  if t in METHODS]
                 for x in imperatives]
                if sub]
    curr_step_hows = dict(zip(list(range(1, len(possible)+1)), [x.strip(' and.') for x in possible]))
    return 'answer_how_to_vague', 0


def specific_how_to(ip):
    # print(f'SPECIFIC ip: {ip}')
    pos = ['VB', 'VBP', 'NN', 'NNS']
    tokens = nltk.pos_tag(nltk.word_tokenize(ip.lower()[ip.find('do')+4:]))
    # print(tokens)
    stop = next(i for i, x in enumerate(tokens) if x[1] in pos)
    return 'answer_how_to_specific', re.sub(r'\s+([,:;-])', r'\1', ' '.join(t[0] for t in tokens[stop:]))


if __name__ == '__main__':
    run()
    # tokens = nltk.pos_tag(nltk.word_tokenize('How do I do that?'))
    # print(tokens)
    # t = [i for i,x in enumerate(tokens) if x[1] in ['VB','VBP']]
    # print(t)
    # if all(tokens[i][0] == 'do' for i in t): print('all "do"!')
    # # print([w[1] for w in tokens])
    # # vb = np.argwhere(np.array([w[1] for w in tokens]) == 'VB') #= [w[1] for w in tokens][::-1].index('VBP') or [w[1] for w in tokens][::-1].index('VB')
    # # except: vb = 0; print('except')
    # # print(tokens[tokens[1] == 'VB'])
    # # print(vb)
    # # print(tokens)
    # tokens = nltk.pos_tag(nltk.word_tokenize('How do do the baking?'))
    # print(tokens)
    # stemmer = nltk.stem.porter.PorterStemmer()
    # print([stemmer.stem(s) for s in [w[0] for w in tokens]])

    # s = 'Pour chicken stock into a large pot, and add ham hocks onion, garlic, red pepper flakes, vinegar, black pepper, and enough water to cover ham hocks. Bring to a boil; reduce heat, and simmer for 1 to 2 hours to create the broth.'
    # specific_how_to(s)

    # recipe = get_recipe('https://www.allrecipes.com/recipe/278180/greek-yogurt-blueberry-lemon-pancakes/')
    # for s in recipe['directions']:
    #     specific_how_to(s)
    #     print('\n')

    # s = 'Add chicken, coat with the marinade, squeeze out excess air, and seal the bag. Marinate in the refrigerator for at least 2 hours.'

    # tokens = nltk.pos_tag(nltk.word_tokenize(s.lower()))
    # for t in tokens:
    #     print(stemmer.stem(t[0]))
    # if t in METHODS or stemmer.stem(t) in METHODS:
    # print(nltk.pos_tag(nltk.word_tokenize('how do i cook eggs')))
    # print(nltk.pos_tag(nltk.word_tokenize('how do i preheat an oven')))
    # VB, VBP, NN, NNS
