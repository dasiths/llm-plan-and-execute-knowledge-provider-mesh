import os
import dotenv

from langchain_openai import AzureChatOpenAI

def get_llm(deployment=None, model=None):
    # load environment variables using dotenv
    dotenv.load_dotenv()

    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    RESOURCE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

    AZURE_OPENAI_DEPLOYMENT_NAME = deployment if deployment is not None \
        else os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    AZURE_OPENAI_MODEL_NAME = model if model is not None \
        else os.getenv("AZURE_OPENAI_MODEL_NAME")

    # print all those env vars, except for the keys
    print(f"AZURE_OPENAI_ENDPOINT={os.getenv('AZURE_OPENAI_ENDPOINT')}")
    print(f"RESOURCE_ENDPOINT={RESOURCE_ENDPOINT}")
    print(f"AZURE_OPENAI_DEPLOYMENT_NAME={AZURE_OPENAI_DEPLOYMENT_NAME}")
    print(f"AZURE_OPENAI_MODEL_NAME={AZURE_OPENAI_MODEL_NAME}")

    llm = AzureChatOpenAI(deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
                        model_name=AZURE_OPENAI_MODEL_NAME,
                        azure_endpoint=RESOURCE_ENDPOINT,
                        openai_api_key=AZURE_OPENAI_API_KEY,
                        api_version="2023-05-15",
                        )

    return llm
