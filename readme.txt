CS 337 Project 3: Conversational Interface for Project 2

Github Repo: https://github.com/nthntmmrmn/CS337-Project3

Team members: Nathan Timmerman, Nicholas Kao, Esther Whang, Batuhan Ergor

Basic goals and how we met them:

1. Recipe retrieval and display (see example above, including "Show me the ingredients list");
--- Any input containing the word "ingredient(s)" receives the ingredient list as output.

2. Navigation utterances ("Go back one step", "Go to the next step", "Take me to the 1st step", "Take me to the n-th step");
--- Any input containing a number or a place (word or number+ending) 
    (e.g., first/1st, second/2nd, third/3rd, fourth/4th, etc.) and the 
    word "step" receives the specified step number as output.
--- Any input containing "next" and "step" receives the next step as output.
--- Any input containing "previous" or "last" or "back" and "step" receives 
    the next step as output.
--- Any input containing the word "direction(s)" receives as output
    the current step of the directions.

3. Vague "how to" questions ("How do I do that?", in which case you can infer a context based on what's parsed for the current step);
--- Vague "how to" questions like "How?" or "How do I do that?" receive either
    a link for a Google search of how to do the method in the step if only one
    method is present. If more than one method is used in the step, the user
    is prompted to choose from a list of possible how-tos. When they select one,
    they receive a Google search link as output. If none of the choices are what
    the user wants, or there are no methods found, the user is prompted to ask
    a specific question.

4. Specific "how to" questions ("How do I <specific technique>?");
--- Specific how-to questions ("How do I [technique]?) receive as
    output a Google search link for "how to [technique]"

5. Name your bot :)
--- RecipeBot9000