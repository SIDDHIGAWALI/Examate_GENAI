import os
import sys
import uuid
from pathlib import Path

import requests
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ui import cards as cardlib

API = os.getenv("CURRICULUMBUDDY_API", "http://127.0.0.1:8000")

st.set_page_config(page_title="CurriculumBuddy", layout="wide")
st.title("CurriculumBuddy")
st.caption("Questions about the AICTE model curriculum, with sources. Data: AICTE UG CSE and Mechanical PDFs.")

if "messages" not in st.session_state:
    st.session_state.messages = []       # the chat history
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "pending" not in st.session_state:
    st.session_state.pending = None      # a tool the agent wants to run and waits for approval


# ---------------------------------------------------------------- talking to the API
def call_api(method, path, payload):
    try:
        response = requests.request(method, API + path, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API at " + API + ". Start it with: uvicorn app.main:app --reload")
    except Exception as e:
        st.error("API error: " + str(e))
    return None


def citations_from_agent(result):
    found = []
    for step in result.get("tools_used", []):
        if isinstance(step.get("result"), dict):
            found = found + step["result"].get("citations", [])
    return found


def add_answer(question, answer, citations, mode, tools=None):
    st.session_state.messages.append({"role": "assistant", "question": question, "content": answer,
                                      "citations": citations, "mode": mode, "tools": tools or [], "rating": None})


def handle_agent_result(question, result):
    if result is None:
        return
    if result["status"] == "waiting_for_approval":
        st.session_state.pending = {"question": question, "tool": result["tool"], "input": result["input"]}
    else:
        st.session_state.pending = None
        add_answer(question, result["answer"], citations_from_agent(result), "agent", result.get("tools_used", []))


def save_feedback(index, rating):
    m = st.session_state.messages[index]
    saved = call_api("POST", "/feedback", {"question": m["question"], "answer": m["content"],
                                           "rating": rating, "mode": m["mode"]})
    if saved:
        m["rating"] = rating


# ---------------------------------------------------------------- page
tab_chat, tab_card = st.tabs(["Ask CurriculumBuddy", "Course card"])

with tab_chat:
    mode = st.radio("Mode", ["Ask (answer with citations)", "Agent (can use the credit calculator)"], horizontal=True)

    for i, m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"]):
            st.write(m["content"])
            if m["role"] == "assistant":
                if m["citations"]:
                    st.caption("Sources")
                    for c in m["citations"]:
                        st.markdown("- " + c["source"] + " · page " + str(c["page"]) + " · " + c["title"])
                if m["tools"]:
                    with st.expander("Tools used"):
                        st.json(m["tools"])
                if m["rating"]:
                    st.caption("Feedback saved: " + ("👍" if m["rating"] == "up" else "👎"))
                else:
                    up, down, _ = st.columns([1, 1, 12])
                    up.button("👍", key="up" + str(i), on_click=save_feedback, args=(i, "up"))
                    down.button("👎", key="down" + str(i), on_click=save_feedback, args=(i, "down"))

    if st.session_state.pending:
        p = st.session_state.pending
        st.warning("The agent wants to run **" + p["tool"] + "** with input `" + str(p["input"]) + "`. Allow it?")
        yes, no, _ = st.columns([1, 1, 10])
        if yes.button("Approve"):
            result = call_api("POST", "/agent", {"thread_id": st.session_state.thread_id, "approve": True})
            handle_agent_result(p["question"], result)
            st.rerun()
        if no.button("Reject"):
            result = call_api("POST", "/agent", {"thread_id": st.session_state.thread_id, "approve": False})
            handle_agent_result(p["question"], result)
            st.rerun()

    question = st.chat_input("Ask about a course, its modules, textbooks or credits")
    if question and not st.session_state.pending:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("Thinking..."):
            if mode.startswith("Ask"):
                result = call_api("POST", "/ask", {"question": question, "k": 3})
                if result:
                    add_answer(question, result["answer"], result["citations"], "ask")
            else:
                result = call_api("POST", "/agent", {"message": question, "thread_id": st.session_state.thread_id})
                handle_agent_result(question, result)
        st.rerun()
    elif question:
        st.info("Please approve or reject the pending tool first.")

with tab_card:
    records = cardlib.load_records()
    cards = cardlib.load_cards()
    by_code = {r["course_code"]: r for r in records}
    ordered = sorted(records, key=lambda r: (r["semester"], r["course_code"]))
    labels = {r["course_code"]: "Sem " + str(r["semester"]) + " · " + r["course_code"] + " · " + r["course_title"] for r in ordered}

    code = st.selectbox("Choose a course", list(labels.keys()), format_func=lambda c: labels[c])
    r = by_code[code]
    ltp = r["l_t_p_credits"]
    card = cards.get(code, {"modules": [], "prerequisites": [], "note": ""})

    st.subheader(r["course_title"])
    st.caption(code + " · Semester " + str(r["semester"]) + " · " + ltp["category"] + " · " + r["branch"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("L-T-P", str(ltp["L"]) + "-" + str(ltp["T"]) + "-" + str(ltp["P"]))
    c2.metric("Credits (AICTE table)", ltp["credits"])
    c3.metric("Credits from L-T-P", cardlib.number_text(ltp["L"] + ltp["T"] + ltp["P"] / 2))
    c4.metric("Contact hours / week", ltp["L"] + ltp["T"] + ltp["P"])

    st.markdown("#### Modules")
    strip = cardlib.module_strip(card["modules"])
    if strip["mode"] == "none":
        st.info("The AICTE document gives no module list for this course.")
    else:
        if strip["mode"] == "proportional":
            st.caption("Bar width = module duration. Total: " + cardlib.number_text(strip["total"]) + " " + strip["unit"] + ".")
        else:
            st.caption("The AICTE document does not give all durations for this course, so the bars are equal width.")
        st.markdown(cardlib.strip_html(strip), unsafe_allow_html=True)
        st.markdown(cardlib.legend_html(strip), unsafe_allow_html=True)

    st.markdown("#### Builds on (earlier semesters)")
    paths = cardlib.prerequisite_paths(code, cards, by_code)
    if paths:
        st.markdown(cardlib.chain_html(paths, code, by_code), unsafe_allow_html=True)
        for line in cardlib.prerequisite_notes(code, cards, by_code):
            st.caption(line)
    else:
        st.write("No earlier-semester prerequisite is recorded for this course.")

    if card["note"]:
        st.info(card["note"])