from abc import ABC, abstractmethod
from openai import OpenAI
from langchain_openai import ChatOpenAI
import os

class FetcherInterface(ABC):
    @abstractmethod
    async def fetch(self, input_data):
        pass

class EmbeddingFetcher(FetcherInterface):
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    async def fetch(self, input_data):
        response = self.client.embeddings.create(input=input_data['name'], model="text-embedding-3-small")
        return {'name': input_data['name'], 'embedding': response.data[0].embedding}

class LinkDecisionFetcher(FetcherInterface):
    def __init__(self, model_name='gpt-4o'):
        self.model = ChatOpenAI(model=model_name)

    async def fetch(self, input_data):
        response = await self.model.predict(f"Should we click this link: {input_data['link_text']}?")
        return {'response': response}
