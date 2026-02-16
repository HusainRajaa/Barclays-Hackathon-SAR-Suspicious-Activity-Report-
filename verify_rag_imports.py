try:
    from langchain_community.vectorstores import FAISS
    print("langchain_community.vectorstores.FAISS imported successfully")
except ImportError as e:
    print(f"langchain_community.vectorstores.FAISS import failed: {e}")

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    print("langchain_huggingface imported successfully")
except ImportError as e:
    print(f"langchain_huggingface import failed: {e}")
