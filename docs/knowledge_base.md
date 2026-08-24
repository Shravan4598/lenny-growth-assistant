# Knowledge Base Design

## Source

The Lenny Growth Assistant uses the public Lenny's Data starter
repository as its primary knowledge source.

Repository:

https://github.com/LennysNewsletter/lennys-newsletterpodcastdata

The starter repository contains AI-friendly Markdown content and an
`index.json` metadata file.

The initial production scope indexes podcast transcripts.

Newsletter content can be enabled through configuration.

## Data Flow

```text
Repository
    ↓
index.json + Markdown files
    ↓
LennyRepositoryLoader
    ↓
Normalized Transcript
    ↓
Cleaner
    ↓
Chunker
    ↓
Embedding Model
    ↓
FAISS Index
    ↓
Retriever