from abc import ABC, abstractmethod
from openai import OpenAI
from langchain_openai import ChatOpenAI
import logging
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModel
import torch
import aiohttp
import os
import re
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

class FetcherInterface(ABC):
    @abstractmethod
    async def fetch(self, input_data):
        self.model = ChatOpenAI(model='gpt-4o')


class EmbeddingFetcher(FetcherInterface):
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    async def fetch(self, input_data):
        response = self.client.embeddings.create(input=input_data['text'], model="text-embedding-3-small")
        return {'text': input_data['text'], 'embedding': response.data[0].embedding}


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


class HTTPFetcher(FetcherInterface):
    async def fetch(self, input_data):
        async with aiohttp.ClientSession() as session:
            async with session.get(input_data['url']) as response:
                html_content = await response.text()
        return {'url': input_data['url'], 'content': html_content}


class URLFetcher(FetcherInterface):
    def __init__(self, model_name='gpt-4o-mini-search-preview'):
        self.model = ChatOpenAI(model=model_name)

    async def fetch(self, input_data):
        company_name = input_data['company_name']
        messages = [
            ("system", "You are an expert in identifying official company websites. Provide the official website URL for the given company name."),
            ("human", company_name)
        ]

        response = await self.model.ainvoke(messages)

        # Extract URL from the response content using a regex pattern
        url_match = re.search(r'(https?://[^\s\)]+)', response.content)
        url = url_match.group(0) if url_match else None

        return {'company_name': company_name, 'url': url}

class IsFinancialReport(FetcherInterface):
    async def fetch(self, input_data):
        page_content = input_data['page_content']

        # Step 1: Extract text from HTML
        soup = BeautifulSoup(page_content, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)

        # Step 2: Chunk text into 200 character segments
        chunks = [text_content[i:i+200] for i in range(0, len(text_content), 200)]

        # Step 3: Embed each chunk using Hugging Face
        tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

        def embed_text(text):
            inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
            with torch.no_grad():
                outputs = model(**inputs)
            return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

        embeddings = [embed_text(chunk) for chunk in chunks]

        # Step 4: Calculate the mean of the embeddings
        mean_embedding = torch.tensor(embeddings).mean(dim=0).numpy()

        return {'mean_embedding': mean_embedding}
