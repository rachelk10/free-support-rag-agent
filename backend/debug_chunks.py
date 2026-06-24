import json
from pathlib import Path

index_path = Path('data/rag/processed/rag_index.json')
if index_path.exists():
    with open(index_path, encoding='utf-8') as f:
        data = json.load(f)
    
    print(f'צ\'אנקים בשמור: {len(data.get("chunks", []))}')
    print()
    
    # בואו ניראה את הצ'אנקים מ-04_curriculum שנשמרו
    for chunk in data['chunks']:
        if '04_curriculum' in chunk['source']:
            print(f"ID: {chunk['id']}")
            print(f"  Text length: {len(chunk['text'])}")
            print(f"  Preview: {chunk['text'][:60]}")
            print()
