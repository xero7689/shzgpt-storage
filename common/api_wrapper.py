import openai


class BaseChatCompleteWrapper():
    def __init__(self, api_key):
        self.vendor = None
        self.api_key = api_key

    def send(self, messages):
        self._preprocess_messages(messages)
        response = self._make_api_request(messages)
        transformed_result = self._process_response(response)
        return transformed_result

    def _preprocess_messages(self, messages):
        pass

    def _make_api_request(self, messages):
        raise NotImplementedError

    def _process_response(self, messages):
        raise NotImplementedError


class OpenAIAPIWrapper(BaseChatCompleteWrapper):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.vendor = openai
        self.vendor.api_key = api_key

    def _preprocess_messages(self, messages):
        return messages

    def _make_api_request(self, messages):
        return self.vendor.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    def _process_response(self, response):
        response = response['choices'][0]['message']['content']
        return response
