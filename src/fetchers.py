from abc import ABC, abstractmethod
from openai import OpenAI
from langchain_openai import ChatOpenAI
import base64
import logging
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModel
import torch
from transformers import pipeline
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


class PDFFetcher(FetcherInterface):
    async def fetch(self, input_data):
        async with aiohttp.ClientSession() as session:
            async with session.get(input_data['url']) as response:
                pdf_content = await response.read()
                encoded_content = base64.b64encode(pdf_content).decode('utf-8')
        return {'url': input_data['url'], 'encoded_content': encoded_content}

class IsFinancialReport(FetcherInterface):
    async def fetch(self, input_data):
        page_content = input_data['page_content']

        # Step 1: Extract text from HTML
        soup = BeautifulSoup(page_content, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)

        # Initialize tokenizer
        tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

        # Step 2: Chunk text into 200 token segments
        tokens = tokenizer(text_content, return_tensors="pt", truncation=False, padding=False).input_ids[0]
        chunks = []
        current_chunk = []
        current_length = 0

        for token in tokens:
            current_chunk.append(token)
            current_length += 1
            if current_length >= 200:
                chunks.append(current_chunk)
                current_chunk = []
                current_length = 0

        if current_chunk:
            chunks.append(current_chunk)

        chunks = [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]

        # Step 3: Embed each chunk using Hugging Face
        tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

        def embed_text(text):
            inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
            with torch.no_grad():
                outputs = model(**inputs)
            return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

        embeddings = [embed_text(chunk) for chunk in chunks]

        # Step 4: Zero-shot classification
        classifier = pipeline("zero-shot-classification")
        main_text = " ".join(chunks)
        result = classifier(main_text, candidate_labels=["financial report", "blog post", "press release"])

        # NOTE:: The financial report is the highest rank, but is at 0.44.
        # We should consider using the tf-idf weighted approach and weight
        # certain terms higher instead of doing the mean. The mean is
        # throwing it off because there so much extra content being fed
        # into it.
        #
        # Also NOTE:: The pdf parser is pretty garbage in terms of formatting.
        # Are there models out there that can extract based on feeding it a
        # pdf directly? Thinking maybe something compatible with the output
        # that an OCR model generates.

        # Determine if the text is a financial report based on a threshold
        threshold = 0.8  # Example threshold
        is_financial_report = result['scores'][result['labels'].index("financial report")] > threshold

        return {'is_financial_report': is_financial_report}
