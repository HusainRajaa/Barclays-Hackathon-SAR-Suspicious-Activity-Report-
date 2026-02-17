try:
    import fpdf
    print("fpdf imported successfully")
except ImportError as e:
    print(f"fpdf import failed: {e}")

try:
    import graphviz
    print("graphviz imported successfully")
except ImportError as e:
    print(f"graphviz import failed: {e}")

try:
    import langchain
    print("langchain imported successfully")
except ImportError as e:
    print(f"langchain import failed: {e}")
