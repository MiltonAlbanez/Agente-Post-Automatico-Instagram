import requests
from typing import Dict, Any


class ReplicateClient:
    PREDICT_URL = (
        "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
    )

    def __init__(self, token: str):
        self.headers = {"Authorization": f"Bearer {token}"}

    def generate_image(self, prompt: str) -> str:
        payload: Dict[str, Any] = {"input": {"prompt": prompt}}
        resp = requests.post(self.PREDICT_URL, headers=self.headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        # Some Replicate models are async; handle both immediate and polling cases
        output = data.get("output")
        if isinstance(output, list) and output:
            return output[0]
        # If not immediately available, try polling the prediction URL
        prediction_url = data.get("urls", {}).get("get")
        if prediction_url:
            for _ in range(30):
                r = requests.get(prediction_url, headers=self.headers, timeout=30)
                r.raise_for_status()
                d = r.json()
                o = d.get("output")
                if isinstance(o, list) and o:
                    return o[0]
        raise RuntimeError("Failed to retrieve generated image URL from Replicate")