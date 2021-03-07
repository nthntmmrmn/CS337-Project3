import requests
from bs4 import BeautifulSoup
from unicodedata import numeric
from big_lists import TOOLS, PRIMARY_METHODS, OTHER_METHODS
import re
import nltk
import string
import json
import numpy as np
from pprint import pprint

# NOTE: add to these if find something that needs added!
measurements = ['teaspoon', 'tablespoon', 'cup', 'quart', 'ounce', 'gallon', 'pint', 'pound', 'dash', 'pinch', 'small',
                'large', 'clove', 'cloves']
containers = ['package', 'carton', 'container', 'jug', 'box']


def num(n):
    '''
    Input: string
    Output: float if string is unicode fraction or number, 0 otherwise
    '''
    try:
        return numeric(n)
    except:
        try:
            return float(n)
        except:
            return 0


def desc_plus_ingredient(ing):
    t = ing['type']
    d = ing['desc']
    if not d:
        return t
    elif nltk.pos_tag(nltk.word_tokenize(d))[-1][1] == 'NNS':
        split = d.rsplit(' ', 1)
        return split[0].strip() + f' {t} ' + split[1].strip() if len(split) > 1 else f' {t.strip()} ' + split[0].strip()
    else:
        return f'{d.strip()} {t.strip()}'


def reconstruct_ingredient(ing):
    a = ing['amount']
    m = ing['measurement']
    t = ing['type']
    d = ing['desc']
    p = ing['prep']
    return ' '.join(f'{a} {m + "(s) of" if m else ""} {desc_plus_ingredient(ing)}{", " + p if p else ""}'.split())


def parse_ingredients_helper(ing):
    '''
    Input: ingredient string
    Output: [amount, measurement, type of ingredient, preparation]
    '''
    regex = re.compile(
        '(' + 'e?s?|'.join(measurements) + ')(?!(?s:.*)(!?(' + 'e?s?|'.join(measurements) + ')))[\s\)](.*)')
    r = re.search(regex, ing)
    regex_other = re.compile(
        '(' + 'e?s?|'.join(containers) + ')(?!(?s:.*)(!?(' + 'e?s?|'.join(containers) + ')))[\s\)](.*)')
    r_other = re.search(regex_other, ing)
    words = ing.split() if r else ing[0:re.search('[^0-9\u00BC-\u00BE\u2150-\u215E\s]+', ing).end()].split()
    amt = sum([num(x) for x in words])

    if r and r_other:
        first_num = re.search("[^\(0-9\u00BC-\u00BE\u2150-\u215E]+(.*)", ing).group(0)
        ws = first_num[0:re.search('[^\(0-9\u00BC-\u00BE\u2150-\u215E\s]+', first_num).end()].split()
        sm = sum([num(x.strip('()')) for x in ws])
        typ = [f'{sm}-{r.group(1)} {r_other.group(1)}', get_type_of_ingredient(r_other.group(4))]
    elif r_other:
        typ = [r_other.group(1), get_type_of_ingredient(r_other.group(4))]
    elif r:
        typ = [r.group(1), get_type_of_ingredient(r.group(4))]
    else:
        r2 = re.search('[0-9\u00BC-\u00BE\u2150-\u215E]+(.*)', ing)
        if r2:
            typ = ['', get_type_of_ingredient(r2.group(1))]
        else:
            typ = ['', get_type_of_ingredient(ing)]
    return [amt, typ]


def parse_ingredients(ing):
    '''
    Input: list of ingredients
    Output: List of list of dicts with keys: [amount, measurement, type of ingredient, rest]
    '''
    flatten = lambda *n: (e for a in n for e in (flatten(*a) if isinstance(a, (tuple, list)) else (a,)))
    lst = [list(flatten(parse_ingredients_helper(x))) for x in ing]
    return [{'amount': v[0], 'measurement': v[1], 'type': v[2], 'desc': v[3], 'prep': v[4]} for v in lst]


def get_type_of_ingredient(text):
    '''
    Input: ingredient string minus amount and measurement
    Output: [type of ingredient, description, preparation]
    '''
    flip = 0
    pos = ['NN', 'JJ', 'NNS', ',', 'VBG']  # 'VBD' 'VBN' 'VBG'
    tokens = nltk.pos_tag(nltk.word_tokenize(text.lower()))
    stop = next((i for i, v in enumerate(tokens) if v[1] not in pos), len(tokens))
    if stop == 0:
        stop = next((i for i, v in enumerate(tokens) if v[1] in pos), len(tokens))
        flip = 1
    type_ing = ' '.join([v[0] for v in tokens[:stop]])
    rest = ' '.join([v[0] for v in tokens[stop:]])
    typ = re.sub(r'\s+([,:;-])', r'\1', type_ing).strip(string.punctuation)
    prep = re.sub(r'\s+([,:;-])', r'\1', rest)

    tokens = nltk.pos_tag(nltk.word_tokenize(typ if not flip else prep))
    if flip: prep = typ

    if len(tokens) > 1:
        do_nns = 1
        try:
            last_nn = len(tokens) - 1 - [w[1] for w in tokens][::-1].index('NN')
        except:
            do_nns = 0
            last_nn = len(tokens) - 1 - [w[1] for w in tokens][::-1].index('NNS')
        try:
            first_jj = [w[1] for w in tokens].index('JJ')
        except:
            first_jj = 0
        if do_nns:
            try:
                last_nns = len(tokens) - 1 - [w[1] for w in tokens][::-1].index('NNS')
            except:
                last_nns = -1
        else:
            last_nns = -1
        try:
            last_vbg = len(tokens) - 1 - [w[1] for w in tokens][::-1].index('VBG')
        except:
            last_vbg = -1
        try:
            vbd = [w[1] for w in tokens].index('VBD')
        except:
            vbd = -1
        if last_nn + 1 == last_nns:
            if first_jj:
                desc = ' '.join([v[0] for v in tokens[first_jj:last_nn]] + [tokens[last_nns][0]])
                typ = tokens[last_nn][0]
            else:
                desc = ' '.join([v[0] for v in tokens[:last_nn]] + [tokens[last_nns][0]])
                typ = tokens[last_nn][0]
        elif last_nn + 1 == last_vbg:
            desc = ' '.join([v[0] for v in tokens[:last_vbg]])
            typ = ' '.join([v[0] for v in tokens[last_vbg:]])
        else:
            if first_jj:
                desc = ' '.join([v[0] for v in tokens[first_jj:last_nn]])
                typ = tokens[last_nn][0]
            else:
                desc = ' '.join([v[0] for v in tokens[:last_nn]])
                typ = tokens[last_nn][0]
        if not vbd == -1: prep += f', {" ".join([v[0] for v in tokens[vbd:]])}'
    elif len(tokens) == 1:
        desc = ''
        typ = tokens[0][0]
    else:
        desc = ''
        typ = ''

    return [typ, re.sub(r'\s+([,:;-])', r'\1', desc), prep]


def get_tools(dirs):
    '''
    Input: list of directions
    Output: list of tools
    '''
    pos = ['NN', 'JJ', ',', 'RB']
    tools = []
    for d in dirs:
        temp_tools = [t for t in TOOLS if t in d.lower()]
        for t in temp_tools:
            tokens = nltk.pos_tag(nltk.word_tokenize(d[0:d.lower().index(t)].lower()))[::-1]
            stop = next((i for i, v in enumerate(tokens) if v[1] not in pos), len(tokens))
            tools.append(re.sub(r'\s+([,:;-])', r'\1', ' '.join([w[0] for w in tokens[:stop][::-1]]) + f' {t}').strip())
    return np.unique(tools)


def get_methods(dirs):
    '''
    Input: list of directions
    Output: dict of primary and secondary methods containing lists
    '''
    flatten = lambda *n: (e for a in n for e in (flatten(*a) if isinstance(a, (tuple, list)) else (a,)))
    primary = list(flatten([[m for m in PRIMARY_METHODS if m in d.lower()] for d in dirs]))
    other = list(flatten([[m for m in OTHER_METHODS if m in d.lower() and m not in primary] for d in dirs]))
    return {'primary': list(np.unique(primary)), 'secondary': list(np.unique(other))}


def get_html(url):
    '''
    Input: string url to an AllRecipes.com recipe page
    Output: BeautifulSoup-parsed document
    '''
    r = requests.get(url)
    return BeautifulSoup(r.text, 'html.parser')


def get_recipe(url):
    '''
    Input: string url to an AllRecipes.com recipe page
    Output: dict containing ingredients and directions
    '''
    soup = get_html(url)
    j = json.loads(soup.find('script', type='application/ld+json').string)[1]
    return {'name': j['name'], 
            'ingredients': j['recipeIngredient'],
            'parsed_ingredients': parse_ingredients(j['recipeIngredient']),
            'directions': [i['text'].strip('\n') for i in j['recipeInstructions']],
            'servings': sum([num(x) for x in j['recipeYield']])}

# ## Example:
## Get base recipe (uncomment one)
# recipe = get_recipe('https://www.allrecipes.com/recipe/173505/big-bs-collard-greens/')
# recipe = get_recipe('https://www.allrecipes.com/recipe/273864/greek-chicken-skewers/')
# recipe = get_recipe('https://www.allrecipes.com/recipe/278180/greek-yogurt-blueberry-lemon-pancakes/')
# recipe = get_recipe('https://www.allrecipes.com/recipe/280509/stuffed-french-onion-chicken-meatballs')
# recipe = get_recipe('https://www.allrecipes.com/recipe/279677/annes-chicken-chilaquiles-rojas/')

## Print name, ingredients, recipe
# pprint(recipe['name'])
# pprint(recipe['ingredients'])
# pprint(recipe['directions'])

## Parse tools and methods
# tools = get_tools(recipe['directions'])
# pprint(tools)
# methods = get_methods(recipe['directions'])
# pprint(methods)

## Parse ingredients
# pi = parse_ingredients(recipe['ingredients'])
# pprint(pi)