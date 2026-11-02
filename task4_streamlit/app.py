"""Streamlit chat UI over the RAG pipeline: streaming tokens, chat history, session state.

Run from the repo root:  streamlit run task4_streamlit/app.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # make `common`, `task2_rag` importable

import streamlit as st

from task2_rag.ingest import DEFAULT_DB_DIR, ingest_paths
from task2_rag.rag import RAG, source_label

st.set_page_config(page_title="Document Q&A", page_icon="📄", layout="centered")
st.title("📄 Chat with your documents")
st.caption("Answers come only from your uploaded files, with page citations.")

# ---- session state -------------------------------------------------------
ss = st.session_state
ss.setdefault("messages", [])  # [{"role", "content", "sources"?}]
ss.setdefault("kb_ready", DEFAULT_DB_DIR.exists() and any(DEFAULT_DB_DIR.iterdir()))

# ---- sidebar: knowledge base + controls ---------------------------------
with st.sidebar:
    st.header("Knowledge base")
    files = st.file_uploader("Upload PDF / TXT / MD", type=["pdf", "txt", "md"], accept_multiple_files=True)
    if st.button("Build knowledge base", disabled=not files, use_container_width=True):
        with st.spinner("Reading, chunking and embedding…"):
            try:
                tmp = Path(tempfile.mkdtemp())
                for f in files:
                    (tmp / f.name).write_bytes(f.getvalue())
                n = ingest_paths([tmp])
                ss.kb_ready, ss.messages = True, []
                st.success(f"Indexed {n} chunks from {len(files)} file(s).")
            except Exception as e:
                st.error(f"Indexing failed: {e}")

    k = st.slider("Passages retrieved per question", 2, 8, 4)
    if st.button("🗑️ Clear chat", use_container_width=True):
        ss.messages = []
        st.rerun()
    st.caption(f"Messages in session: {len(ss.messages)}")


def render_sources(sources: list[str]) -> None:
    with st.expander("Sources"):
        for s in sources:
            st.markdown(f"- {s}")


# ---- replay history ------------------------------------------------------
for m in ss.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sources"):
            render_sources(m["sources"])

# ---- new question --------------------------------------------------------
if not ss.kb_ready:
    st.info("Upload documents in the sidebar and click **Build knowledge base** to begin.")

if prompt := st.chat_input("Ask a question about your documents", disabled=not ss.kb_ready):
    ss.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            docs, tokens = RAG(k=k).ask_stream(prompt)
            answer = st.write_stream(tokens)  # streams tokens live and returns the full text
            sources = list(dict.fromkeys(source_label(d) for d in docs))
            render_sources(sources)
            ss.messages.append({"role": "assistant", "content": answer, "sources": sources})
        except Exception as e:
            st.error(f"Something went wrong: {e}")
