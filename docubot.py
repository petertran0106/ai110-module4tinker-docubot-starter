"""
Core DocuBot class responsible for:
- Loading documents from the docs/ folder
- Building a simple retrieval index (Phase 1)
- Retrieving relevant snippets (Phase 1)
- Supporting retrieval only answers
- Supporting RAG answers when paired with Gemini (Phase 2)
"""

import os
import glob

class DocuBot:
    def __init__(self, docs_folder="docs", llm_client=None):
        """
        docs_folder: directory containing project documentation files
        llm_client: optional Gemini client for LLM based answers
        """
        self.docs_folder = docs_folder
        self.llm_client = llm_client

        # Load documents into memory
        self.documents = self.load_documents()  # List of (filename, text)

        # Split each document into paragraph-level chunks for finer retrieval
        self.chunks = self.chunk_documents(self.documents)  # List of (filename, paragraph_text)

        # Build a retrieval index (implemented in Phase 1)
        self.index = self.build_index(self.chunks)

    # -----------------------------------------------------------
    # Document Loading
    # -----------------------------------------------------------

    def load_documents(self):
        """
        Loads all .md and .txt files inside docs_folder.
        Returns a list of tuples: (filename, text)
        """
        docs = []
        pattern = os.path.join(self.docs_folder, "*.*")
        for path in glob.glob(pattern):
            if path.endswith(".md") or path.endswith(".txt"):
                with open(path, "r", encoding="utf8") as f:
                    text = f.read()
                filename = os.path.basename(path)
                docs.append((filename, text))
        return docs

    # -----------------------------------------------------------
    # Chunking (paragraph-based)
    # -----------------------------------------------------------

    def chunk_documents(self, documents):
        """
        Splits each document into paragraph chunks by splitting on blank lines
        (one or more consecutive empty lines).

        Returns a flat list of (filename, paragraph_text) tuples, one per
        non-empty paragraph. Short paragraphs (fewer than 5 words) are dropped
        to avoid indexing headers or stray lines.

        Strategy chosen: blank-line splitting keeps related sentences together
        without needing any external libraries.
        """
        chunks = []
        for filename, text in documents:
            # Split on one-or-more blank lines
            paragraphs = [p.strip() for p in text.split("\n\n")]
            for para in paragraphs:
                # Skip near-empty paragraphs like lone headings or blank lines
                if len(para.split()) >= 5:
                    chunks.append((filename, para))
        return chunks

    # -----------------------------------------------------------
    # Index Construction (Phase 1)
    # -----------------------------------------------------------

    def build_index(self, chunks):
        """
        TODO (Phase 1):
        Build a tiny inverted index mapping lowercase words to the chunks
        (filename strings) they appear in. Now receives paragraph-level chunks
        rather than whole documents.

        Example structure:
        {
            "token": ["AUTH.md", "API_REFERENCE.md"],
            "database": ["DATABASE.md"]
        }

        Keep this simple: split on whitespace, lowercase tokens,
        ignore punctuation if needed.
        """
        index = {}
        # TODO: consider stripping punctuation more thoroughly (e.g. using re.sub)
        for filename, text in chunks:
            for raw_token in text.split():
                token = raw_token.lower().strip(".,!?;:\"'()[]")
                if token not in index:
                    index[token] = []
                if filename not in index[token]:
                    index[token].append(filename)
        return index

    # -----------------------------------------------------------
    # Scoring and Retrieval (Phase 1)
    # -----------------------------------------------------------

    def score_document(self, query, text):
        """
        TODO (Phase 1):
        Return a simple relevance score for how well the text matches the query.

        Suggested baseline:
        - Convert query into lowercase words
        - Count how many appear in the text
        - Return the count as the score
        """
        # TODO: improve by weighting rare words more (e.g. TF-IDF)
        text_lower = text.lower()
        score = 0
        for raw_token in query.split():
            token = raw_token.lower().strip(".,!?;:\"'()[]")
            if token and token in text_lower:
                score += 1
        return score

    def retrieve(self, query, top_k=3):
        """
        TODO (Phase 1):
        Use the index and scoring function to select top_k relevant document snippets.

        Return a list of (filename, text) sorted by score descending.
        """
        # TODO: use the index to skip chunks with zero query-word overlap
        # before scoring, for efficiency on large corpora
        scored = []
        for filename, text in self.chunks:
            score = self.score_document(query, text)
            if score > 0:
                scored.append((score, filename, text))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [(filename, text) for _, filename, text in scored]
        return results[:top_k]

    # -----------------------------------------------------------
    # Answering Modes
    # -----------------------------------------------------------

    def answer_retrieval_only(self, query, top_k=3):
        """
        Phase 1 retrieval only mode.
        Returns raw snippets and filenames with no LLM involved.
        """
        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        formatted = []
        for filename, text in snippets:
            formatted.append(f"[{filename}]\n{text}\n")

        return "\n---\n".join(formatted)

    def answer_rag(self, query, top_k=3):
        """
        Phase 2 RAG mode.
        Uses student retrieval to select snippets, then asks Gemini
        to generate an answer using only those snippets.
        """
        if self.llm_client is None:
            raise RuntimeError(
                "RAG mode requires an LLM client. Provide a GeminiClient instance."
            )

        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        return self.llm_client.answer_from_snippets(query, snippets)

    # -----------------------------------------------------------
    # Bonus Helper: concatenated docs for naive generation mode
    # -----------------------------------------------------------

    def full_corpus_text(self):
        """
        Returns all documents concatenated into a single string.
        This is used in Phase 0 for naive 'generation only' baselines.
        """
        return "\n\n".join(text for _, text in self.documents)
