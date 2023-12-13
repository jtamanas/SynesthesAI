from LLM.base import BaseLLM
import google.generativeai as genai
from google.generativeai.types import safety_types
import streamlit as st


class Gemini(BaseLLM):
    def __init__(self, model: str = "models/gemini-pro") -> None:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        models = [
            m
            for m in genai.list_models()
            if ("generateContent" in m.supported_generation_methods) and (m.name == model)
        ]
        model = genai.GenerativeModel(models[0].name)

        harm_categories = [
            # "DEROGATORY",
            "TOXICITY",
            "VIOLENCE",
            "SEXUAL",
            "MEDICAL",
            "DANGEROUS",
            "HARASSMENT",
            "HATE_SPEECH",
            "SEXUALLY_EXPLICIT",
            "DANGEROUS_CONTENT"
        ]
        self.safety_settings = [
            {
                "category": getattr(
                    safety_types.HarmCategory, f"HARM_CATEGORY_{category}"
                ),
                "threshold": safety_types.HarmBlockThreshold.BLOCK_NONE,
            }
            for category in harm_categories
        ]

        super().__init__(model=model)

    def complete(
        self, prompt: str, temperature: float = 1.0, max_tokens: int = 300
    ) -> str:
        response = self.model.generate_content(
            prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
            safety_settings=self.safety_settings,
        )
        result = response.text
        if result is None:
            print(response)
        return result
