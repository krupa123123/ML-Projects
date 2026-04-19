import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from audio_input import AudioRecorder
from analyzer import CommunicationAnalyzer
from metrics_db import ProgressDB
import os
import tempfile

# Page config
st.set_page_config(
    page_title="Communication Trainer", 
    page_icon="🎯",
    layout="wide"
)

# Initialize session state
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "recorder" not in st.session_state:
    st.session_state.recorder = None

def init_recorder():
    """Lazy load model (heavy operation)"""
    if st.session_state.recorder is None:
        with st.spinner("Loading AI models... (one-time, ~20 seconds)"):
            st.session_state.recorder = AudioRecorder(model_size="base")
    return st.session_state.recorder

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.api_key)
    if api_key:
        st.session_state.api_key = api_key
    
    st.markdown("---")
    st.markdown("**How to use:**")
    st.markdown("1. Enter API key")
    st.markdown("2. Choose topic")
    st.markdown("3. Record 30-120 seconds")
    st.markdown("4. Get AI feedback")
    st.markdown("5. Track progress over time")

# Main
st.title("🎯 AI Communication Trainer")
st.markdown("*Practice technical explanations. Get feedback. Improve visibly.*")

if not st.session_state.api_key:
    st.warning("👈 Enter your OpenAI API key in the sidebar to begin")
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["🎙️ Practice", "📊 History", "📈 Progress"])

with tab1:
    st.header("Record Your Explanation")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        topic = st.text_input(
            "What will you explain?", 
            placeholder="e.g., 'How backpropagation works in neural networks'"
        )
    with col2:
        duration = st.slider("Duration (sec)", 30, 120, 60)
    
    if not topic:
        st.info("Enter a topic above to enable recording")
        st.stop()
    
    # Recording section
    if st.button("🔴 Start Recording", type="primary", use_container_width=True):
        try:
            recorder = init_recorder()
            result = recorder.record_and_transcribe(duration)
            
            st.session_state.last_result = result
            st.session_state.last_topic = topic
            
            st.success("✓ Transcribed!")
            st.text_area("Your transcript", result["full_text"], height=150)
            
        except Exception as e:
            st.error(f"Recording failed: {e}")
            st.info("Try uploading an audio file instead (feature coming soon)")
            st.stop()
    
    # Analysis section
    if "last_result" in st.session_state and st.button("🤖 Get AI Feedback", type="secondary"):
        with st.spinner("Analyzing with GPT..."):
            analyzer = CommunicationAnalyzer(st.session_state.api_key)
            feedback = analyzer.analyze(
                st.session_state.last_result["full_text"],
                st.session_state.last_result["words"],
                st.session_state.last_result["duration"]
            )
            
            # Display metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Clarity", f"{feedback.clarity_score}/10")
            m2.metric("Structure", f"{feedback.structure_score}/10")
            m3.metric("Speaking Rate", f"{feedback.wpm:.0f} WPM")
            m4.metric("Filler Words", sum(feedback.filler_count.values()))
            
            # Filler breakdown
            if feedback.filler_count:
                st.caption("Filler words detected:")
                st.write(", ".join([f"{k}: {v}" for k, v in feedback.filler_count.items()]))
            
            # Suggestions
            st.subheader("💡 Improvements")
            for i, sug in enumerate(feedback.suggestions, 1):
                st.write(f"{i}. {sug}")
            
            # Rewritten version
            st.subheader("✍️ Suggested Rewrite")
            st.info(feedback.rewritten_version)
            
            # Save to DB
            db = ProgressDB()
            db.save(
                topic=st.session_state.last_topic,
                duration=duration,
                word_count=len(st.session_state.last_result["words"]),
                wpm=feedback.wpm,
                clarity=feedback.clarity_score,
                structure=feedback.structure_score,
                filler_words=feedback.filler_count,
                suggestions=feedback.suggestions,
                transcript=st.session_state.last_result["full_text"]
            )
            st.success("✓ Saved to progress database")

with tab2:
    st.header("Session History")
    db = ProgressDB()
    sessions = db.get_all()
    
    if not sessions:
        st.info("No sessions yet. Complete your first practice above!")
    else:
        df = pd.DataFrame(sessions)
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        df['filler_words'] = df['filler_words'].apply(lambda x: sum(json.loads(x).values()) if x else 0)
        
        display_df = df[['timestamp', 'topic', 'clarity', 'structure', 'wpm', 'filler_words', 'top_suggestion']]
        display_df.columns = ['Date', 'Topic', 'Clarity', 'Structure', 'WPM', 'Fillers', 'Key Tip']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)

with tab3:
    st.header("Progress Over Time")
    db = ProgressDB()
    sessions = db.get_all()
    
    if len(sessions) < 2:
        st.info("Complete at least 2 sessions to see trends")
    else:
        df = pd.DataFrame(sessions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Scores over time
        ax1.plot(df['timestamp'], df['clarity'], 'o-', label='Clarity', color='#2ecc71')
        ax1.plot(df['timestamp'], df['structure'], 's-', label='Structure', color='#3498db')
        ax1.set_ylim(0, 10)
        ax1.legend()
        ax1.set_title("Communication Scores")
        ax1.grid(True, alpha=0.3)
        
        # WPM over time
        ax2.plot(df['timestamp'], df['wpm'], 'o-', color='#e74c3c')
        ax2.axhline(y=150, color='gray', linestyle='--', alpha=0.5, label='Fast (150 WPM)')
        ax2.axhline(y=120, color='green', linestyle='--', alpha=0.5, label='Optimal (120 WPM)')
        ax2.legend()
        ax2.set_title("Speaking Rate (WPM)")
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Stats
        st.subheader("Summary Statistics")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Sessions", len(df))
        c2.metric("Avg Clarity", f"{df['clarity'].mean():.1f}")
        c3.metric("Avg WPM", f"{df['wpm'].mean():.0f}")

import json  # Add this import at top if not present