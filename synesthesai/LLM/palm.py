from LLM.base import BaseLLM
import google.generativeai as palm
from google.generativeai.types import safety_types
import streamlit as st

class PaLM(BaseLLM):
    def __init__(self, model: str = "models/text-bison-001") -> None:
        palm.configure(api_key=st.secrets["PALM_API_KEY"])
        models = [
            m for m in palm.list_models() 
            if ('generateText' in m.supported_generation_methods) 
            and (m.name == model)
        ]
        model = models[0].name
        
        harm_categories = [
            "DEROGATORY",
            "TOXICITY",
            "SEXUAL",
            "VIOLENCE", 
            "DANGEROUS",
            "MEDICAL", 
        ]
        self.safety_settings = [
            {
                "category": getattr(safety_types.HarmCategory, f"HARM_CATEGORY_{category}"),
                "threshold": safety_types.HarmBlockThreshold.BLOCK_NONE,
            }
            for category in harm_categories
        ]
        
        super().__init__(model=model)
        
    def complete(self, prompt: str, temperature: float=1.0, max_tokens: int=300) -> str:
        print("prompt:", prompt)
        print("max_tokens:", max_tokens)
        print("temperature:", temperature)
        response = palm.generate_text(
            model=self.model, 
            prompt=prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
            safety_settings=self.safety_settings
        )
        
        return response.result
