import json
from typing import List
from knowledge_provider import KnowledgeProvider

def get_catalog() -> List[KnowledgeProvider]:
    file_path = "catalog.json"
    with open(file_path, 'r') as catalog_file:
        file_contents = catalog_file.read()
        print(file_contents)
        catalog_data = json.loads(file_contents)

    providers = []

    for config in catalog_data:
        name = config["name"]
        description = config["description"]
        provider_url = config["provider_url"]

        service = KnowledgeProvider(name=name, description=description, url=provider_url)
        providers.append(service)

    return providers
