"""Currently, Spotify search will return *a* result, whether it's good or bad. We need a way of rating these results and filtering out bad ones."""

from difflib import SequenceMatcher
from examples import positive_examples, negative_examples
import re 


print("Positive examples:")
for true, typo in positive_examples.items():
    print(true, ": ", typo)
    print("Simple: ", SequenceMatcher(a=true, b=typo).ratio())
    true = re.sub("[\(\[].*?[\)\]]", "", true)
    typo = re.sub("[\(\[].*?[\)\]]", "", typo)
    print("Ignoring (): ", SequenceMatcher(a=true, b=typo).ratio())
    print()

print("_____________________________")
print("Negative examples:")
for true, wrong in negative_examples.items():
    print(true, ": ", wrong)
    print("Simple: ", SequenceMatcher(a=true, b=wrong).ratio())
    true = re.sub("[\(\[].*?[\)\]]", "", true)
    wrong = re.sub("[\(\[].*?[\)\]]", "", wrong)
    print("Ignoring (): ", SequenceMatcher(a=true, b=wrong).ratio())
    print()
    
