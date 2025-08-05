import replicate
import requests

class ReplicateClient:
    def __init__(self):
        self.client = replicate.Client()

    def generate_image(self, prompt, parameters):
        output_url = self.client.run(
            "google/imagen-4-fast",
            input={"prompt": prompt, **parameters}
        )
        # The output is a single URL string for the generated image
        if not output_url:
            raise RuntimeError("No image URL returned from Replicate API")
        response = requests.get(output_url)
        response.raise_for_status()
        return response.content
