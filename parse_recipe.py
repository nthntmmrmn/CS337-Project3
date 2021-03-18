import requests
from bs4 import BeautifulSoup
from unicodedata import numeric
import json

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
            'directions': [i['text'].strip('\n') for i in j['recipeInstructions']],
            }

### Examples:
# recipe = get_recipe('https://www.allrecipes.com/recipe/173505/big-bs-collard-greens/')
# recipe = get_recipe('https://www.allrecipes.com/recipe/273864/greek-chicken-skewers/')
# recipe = get_recipe('https://www.allrecipes.com/recipe/278180/greek-yogurt-blueberry-lemon-pancakes/')
# recipe = get_recipe('https://www.allrecipes.com/recipe/280509/stuffed-french-onion-chicken-meatballs')
# recipe = get_recipe('https://www.allrecipes.com/recipe/279677/annes-chicken-chilaquiles-rojas/')