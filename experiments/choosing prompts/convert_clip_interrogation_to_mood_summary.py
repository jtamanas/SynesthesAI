"""CLIP Interrogation can result in some goofy descriptions sometimes. Use a (cheap) LLM call to make it less silly before passing on to playlist recommendation."""

import google.generativeai as genai

import os
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import matplotlib.pyplot as plt  # not in requirements.txt

# Set API key
genai.config(api_key=os.environ["PALM_API_KEY"]

# Define the description, engines, prompts, and temperatures
description = "a cartoon snail with a colorful shell on its back, snail, elon musk as slimy mollusk, nacre, art of angrysnail, snail shell, transparent goo, nacre colors, colourful slime, gary, snail in the style of nfl logo, inkscape, it's name is greeny, slimy, cell shaded cartoon, turbo"
engines = [
    "text-davinci-003",
    "text-davinci-002",
    "text-curie-001",
    # "text-babbage-001",
    # "text-ada-001",
]
prompts = [
    # "Summarize the following description focusing on tone and emotion",
    # "Give a brief summary of the following artistic description",
    "Rephrase the following description of an image. Be sure to include the emotions evoked by said image",
    "Rewrite this description of an image. Focus on specific feelings and emotions evoked",
]
temperatures = [0.5, 0.7, 1.0, 1.2]

# Create a DataFrame for all combinations of engines, prompts, and temperatures
df = pd.DataFrame(
    [
        (engine, prompt, temperature)
        for engine in engines
        for prompt in prompts
        for temperature in temperatures
    ],
    columns=["engine", "prompt", "temperature"],
)

# Add the common description to all rows
df["description"] = description


def get_summary(row):
    response = openai.Completion.create(
        engine=row["engine"],
        prompt=f"{row['prompt']}: '{row['description']}'",
        temperature=row["temperature"],
        max_tokens=60,
    )
    return response.choices[0].text.strip()


# Apply the function to each row in your DataFrame
df["summary"] = df.apply(get_summary, axis=1)

# Check the DataFrame
print(df)

# Save the DataFrame as a PDF report
fig, ax = plt.subplots(figsize=(12, 4))
ax.axis("tight")
ax.axis("off")
the_table = ax.table(
    cellText=df.values, colLabels=df.columns, cellLoc="center", loc="center"
)

pp = PdfPages("Summarization_report.pdf")
pp.savefig(fig, bbox_inches="tight")
pp.close()


# My fav for starry night is text-davinci-003 with temp=0.5
# My fav for the cartoon snail is text-curie-001 with temp=1.2
# This also performed well on starry night, so I'm going to try it out


# Davinci does quite well with  "Rewrite this description of an image. Focus on the feelings and emotions evoked"
# I'm going to try this out with temp=0.9
