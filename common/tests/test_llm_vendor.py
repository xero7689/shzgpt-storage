"""
import pytest

from common.llm_vendor import OpenAILLM

@pytest.fixture
def llm():
    api_key = ''
    return OpenAILLM(api_key)


def test_openai_gpt_35_send(llm):
    messages=[{"role": "user", "content": "Say this is a test"}]
    llm.send(messages)
    print(llm.response_content)
"""
