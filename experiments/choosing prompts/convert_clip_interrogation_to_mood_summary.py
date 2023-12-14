"""Use gemini vision to get the vibes from the image."""


from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from ...handler.image import ImageHandler


# Set API key


with open('cartoon_snail.png', 'rb') as f:
    model = ImageHandler(BytesIO(f.read()))

# Define the description, engines, prompts, and temperatures
prompts = [
    "Write a very brief description of this picture. Focus on specific emotions, aesthetics, and genres. Feel free to add details of any musical genres it may invoke. Really focus on the emotional response and less so on the objective reality. Write no more than two sentences.",
    "Do not describe this picture. Instead focus on specific emotions, aesthetics, and genres. Feel free to add details of any musical genres it may invoke. Really focus on the emotional response and less so on the objective reality. Write no more than two sentences.",
    "I want a playlist built around this image. What feelings does it evoke? What kind of genres and which musical artists would be appropriate?",
    "I'm blind, but a friend said I'd love this image. I'm wondering if I could make a playlist that would allow me to experience the same feelings that seeing this image would. What feelings does this image evoke? What kind of genres and which musical artists would be appropriate?",
    
]
temperatures = [0.25, 0.5, 0.7, 0.85, 1.0]

# Create a DataFrame for all combinations of engines, prompts, and temperatures
df = pd.DataFrame(
    [
        (prompt, temperature)
        for prompt in prompts
        for temperature in temperatures
    ],
    columns=[ "prompt", "temperature"],
)


def get_summary(row):
    model.description_prompt = row["prompt"]
    model.temperature = row["temperature"]
    response = model.describe()
    return response.strip()


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

