import chromadb

c = chromadb.PersistentClient('./data/chroma').get_collection('sr11_7_docs')
print(f'Total chunks: {c.count()}')

r = c.get(limit=5, include=['documents', 'metadatas'])
for i, (doc, meta) in enumerate(zip(r['documents'], r['metadatas'])):
    print(f'--- Chunk {i+1} ---')
    print(f"Doc: {meta['doc']} | Page: {meta['page']} | Section: {meta['section']}")
    print(doc[:300])
    print()
