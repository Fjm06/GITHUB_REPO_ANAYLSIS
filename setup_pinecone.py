import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

print("🌲 Pinecone Setup Script")
print("=" * 50)

# Get API key
api_key = os.getenv('PINECONE_API_KEY')

if not api_key:
    print("❌ Error: PINECONE_API_KEY not found in .env")
    exit(1)

print("✓ API Key found")

# Initialize Pinecone
try:
    pc = Pinecone(api_key=api_key)
    print("✓ Connected to Pinecone")
except Exception as e:
    print(f"❌ Error connecting: {e}")
    exit(1)

# List existing indexes
print("\n📋 Checking existing indexes...")
existing_indexes = pc.list_indexes()

if existing_indexes:
    print(f"Found {len(existing_indexes)} existing index(es):")
    for idx in existing_indexes:
        print(f"  - {idx['name']} (dimension: {idx.get('dimension', 'N/A')})")
else:
    print("No existing indexes found")

# Index configuration
INDEX_NAME = "decoderbot"
DIMENSION = 384  # sentence-transformers/all-MiniLM-L6-v2
METRIC = "cosine"

print(f"\n🔧 Index Configuration:")
print(f"  Name: {INDEX_NAME}")
print(f"  Dimension: {DIMENSION}")
print(f"  Metric: {METRIC}")

# Check if index already exists
index_exists = any(idx['name'] == INDEX_NAME for idx in existing_indexes)

if index_exists:
    print(f"\n✓ Index '{INDEX_NAME}' already exists!")
    print("You can use it directly in the app.")
else:
    print(f"\n📝 Creating index '{INDEX_NAME}'...")
    
    try:
        # Create serverless index (free tier)
        pc.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            metric=METRIC,
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
        print(f"✓ Index '{INDEX_NAME}' created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        print("\nTroubleshooting:")
        print("1. Check if you're on free tier (only 1 index allowed)")
        print("2. Try deleting existing indexes from Pinecone dashboard")
        print("3. Or use existing index name in the app")
        exit(1)

print("\n" + "=" * 50)
print("✅ Setup Complete!")
print(f"\nYour Pinecone index '{INDEX_NAME}' is ready to use.")
print("\nNext steps:")
print("1. The Streamlit app will automatically use Pinecone")
print("2. Add repositories and they'll be stored in Pinecone")
print("3. Enjoy cloud-based vector search!")
