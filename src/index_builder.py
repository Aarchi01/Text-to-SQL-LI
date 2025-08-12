from llama_index.core import VectorStoreIndex, Document 
#from llama_index.llms.openai import OpenAI
#import os
#from dotenv import load_dotenv

#load_dotenv()
#llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), temperature=0)

def build_index(schema_text: str) -> VectorStoreIndex:
    """
    This builds a simple LlamaIndex vector index from full schema text.
    """
    doc = Document(text=schema_text)
    return VectorStoreIndex.from_documents([doc])