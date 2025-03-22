from openai import OpenAI
from langchain_openai import ChatOpenAI
import os

class EmbeddingFetcher:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    async def fetch_embedding(self, name):
        response = self.client.embeddings.create(input=name, model="text-embedding-3-small")
        return {'name': name, 'embedding': response.data[0].embedding}

class LinkDecisionFetcher:
    def __init__(self, model_name='gpt-4o'):
        self.model = ChatOpenAI(model=model_name)

    async def fetch_decision(self, link_text):
        response = await self.model.predict(f"Should we click this link: {link_text}?")
        return {'response': response}
