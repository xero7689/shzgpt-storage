from common.llm_vendor import OpenAI


class OpenAILLM:
    def create_openai_gpt_model(self, api_key):
        return OpenAI(api_key)


def llm_factory(vendor):
    raise NotImplementedError("Unimplement LLM vendor")
