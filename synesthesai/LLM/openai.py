from LLM.base import BaseLLM
import openai
import streamlit as st

class OpenAI(BaseLLM):
    def __init__(self, model: str = "text-davinci-003") -> None:
        super().__init__(model=model)
        openai.api_key = st.secrets["OPENAI_API_KEY"]
    
    def complete(self, prompt: str, temperature: float=1.0, max_tokens: int=300) -> str:
        response =  openai.Completion.create(
            engine=self.model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            n=1,
            stop=None,
        )
        return response.choices[0].text.strip()