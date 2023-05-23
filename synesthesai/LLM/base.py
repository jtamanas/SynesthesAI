from abc import ABC, abstractmethod

class BaseLLM(ABC):
    def __init__(self, model: str) -> None:
        self.model = model
        pass
    
    @abstractmethod
    def complete(self, prompt: str, temperature: float=1.0, max_tokens: int=300) -> str:
        pass