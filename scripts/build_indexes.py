import argparse
import os
import glob
from chromadb import Client
from chromadb.config import Settings
from core.settings import load_settings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="data/*.md")
    parser.add_argument("--tags", default="UN-Habitat Kuwait")
    args = parser.parse_args()

    settings = load_settings()
    directory = os.path.expanduser(settings.rag.persist_dir)
    os.makedirs(directory, exist_ok=True)
    client = Client(Settings(persist_directory=directory))
    if settings.rag.collection not in [c.name for c in client.list_collections()]:
        client.create_collection(settings.rag.collection)
    collection = client.get_collection(settings.rag.collection)

    files = sorted(glob.glob(args.path))
    ids, docs, metas = [], [], []
    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as handle:
            text = handle.read()
        ids.append(filepath)
        docs.append(text)
        metas.append({"source": filepath, "tags": args.tags})
    if ids:
        collection.upsert(ids=ids, documents=docs, metadatas=metas)
        print(f"Ingested {len(ids)} docs.")
    else:
        print("No files matched.")


if __name__ == "__main__":
    main()
