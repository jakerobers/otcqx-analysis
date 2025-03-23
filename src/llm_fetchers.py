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
        response = self.client.embeddings.create(input=input_data['text'], model="text-embedding-3-small")
        return {'text': input_data['text'], 'embedding': response.data[0].embedding}

class DetermineFinancialLink(FetcherInterface):
    def __init__(self, model_name='gpt-4o'):
        self.model = ChatOpenAI(model=model_name)

    async def fetch(self, potential_links):
        prompt = (
            "From the following list of links, identify the one that most likely leads to Investor Relations, "
            "Financial Documents, or any page that could contain a 10-K report. "
            "Return the link exactly as provided:\n" +
            "\n".join([link['text'] for link in potential_links])
        )
        response = await self.model.predict(prompt)
        return {'response': response}

class GetCompanyDescription(FetcherInterface):
    def __init__(self, model_name='gpt-4o'):
        self.model = ChatOpenAI(model=model_name)

    async def fetch(self, company_name):
        messages = [
            ("system", "You are an expert in company identification. Please help the customer with their question."),
            ("human", company_name)
        ]

        response = await self.model.ainvoke(messages)
        return {'company_name': company_name, 'description': response.content}
