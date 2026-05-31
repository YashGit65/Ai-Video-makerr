from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
load_dotenv()

api2 = os.getenv("api2")

client = InferenceClient(
    provider="nscale",
    api_key=api2
)
