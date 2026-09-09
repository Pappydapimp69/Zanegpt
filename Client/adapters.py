import os

class OpenAIAdapter:
    def __init__(self, model):
        from openai import OpenAI
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = model

    def complete(self, system, user):
        r = self.client.responses.create(model=self.model, instructions=system, input=user)
        return r.output_text

class AnthropicAdapter:
    def __init__(self, model):
        import anthropic
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model

    def complete(self, system, user):
        r = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(block.text for block in r.content if getattr(block, "type", None) == "text")

def make_adapter(provider, model):
    provider = provider.lower()
    if provider == "openai":
        return OpenAIAdapter(model)
    if provider == "anthropic":
        return AnthropicAdapter(model)
    raise ValueError("Unsupported provider: " + provider)
