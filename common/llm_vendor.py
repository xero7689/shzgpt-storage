from abc import ABC, abstractclassmethod

from openai import OpenAI

class LLMVendorConfig(ABC):
    @abstractclassmethod
    def get_config(self):
        pass


class LLMVendor(ABC):
    @abstractclassmethod
    def __init__(self, api_key):
        self._api_key = api_key

    @abstractclassmethod
    def send(self, messages):
        pass

    @abstractclassmethod
    def _preprocess_messages(self, messages):
        pass

    @abstractclassmethod
    def _make_api_request(self, messages):
        pass

    @abstractclassmethod
    def _process_response(self):
        pass

class OpenAILLM(LLMVendor):
    def __init__(self, api_key, model="gpt-3.5-turbo"):
        super().__init__(api_key)
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.response_transformers = []

    def send(self, messages: list[dict]):
        messages = self._preprocess_messages(messages)
        self.response = self._make_api_request(messages)

    def stream_send(self, messages: list[dict]):
        stream = self._make_api_request(messages, stream=True)
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    @property
    def response_content(self) -> str:
        choices = getattr(self.response, 'choices', [])
        message = getattr(choices[0], 'message', {})
        content = getattr(message, 'content', 'Empty chat response')
        return content

    @property
    def response_tokens(self) -> int:
        usage = getattr(self.response, 'usage', {})
        completion_tokens = getattr(usage, 'completion_tokens', 0)
        return completion_tokens

    def _preprocess_messages(self, messages):
        """
        Formats a list of Chat object from models into a request list
        to be used for querying Open AI's Chat GPT completion API endpoint.

        Args:
            chats (list): A list of chat objects containing conversation data.

        Returns:
            list: A request list formatted to be sent to the Chat GPT completion API endpoint.
        """
        processed_messages = []
        for message in messages:
            processed_messages.append(
                {"role": message["role"], "content": message["content"]}
            )
        return processed_messages

    def _make_api_request(self, messages, stream=False):
        return self.client.chat.completions.create(
            model=self.model, messages=messages, stream=stream
        )

    def _process_response(self):
        return self.response
