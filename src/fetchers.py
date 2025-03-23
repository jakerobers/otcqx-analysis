from abc import ABC, abstractmethod
from browser_use import Agent, Controller, ActionResult
from browser_use.browser.browser import Browser, BrowserConfig
from openai import OpenAI
from langchain_openai import ChatOpenAI
import os
from playwright.async_api import async_playwright

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


class URLFetcher(FetcherInterface):
    def __init__(self):
        pass

    async def fetch(self, input_data):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto("https://www.google.com")

            # Accept cookies if visible
            try:
                await page.click('#L2AGLb', timeout=2000)
            except:
                pass

            await page.fill('input[name="q"]', input_data['company_name'])
            await page.keyboard.press('Enter')

            await page.wait_for_selector('h3')
            element = await page.query_selector('h3')
            link = await element.evaluate("el => el.closest('a').href")

            await browser.close()
            return {'company_name': input_data['company_name'], 'url': link}
