import openai
import json
import re
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class CommunicationFeedback:
    clarity_score: int
    structure_score: int
    filler_count: Dict[str, int]
    suggestions: List[str]
    rewritten_version: str
    wpm: float

class CommunicationAnalyzer:
    FILLER_WORDS = ["um", "uh", "like", "you know", "so", "actually", "basically", "literally", "i mean", "sort of"]
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        
        self.system_prompt = """You are an elite communication coach analyzing spoken technical explanations.

Evaluate this transcript and return JSON with:
- clarity_score: 1-10 (are ideas expressed directly and understandably?)
- structure_score: 1-10 (clear opening, logical flow, strong conclusion?)
- suggestions: array of 3 specific, actionable improvements
- rewritten_version: the same content rephrased for maximum clarity while keeping the speaker's authentic voice

Be honest but constructive. Technical audiences value precision over polish."""
    
    def count_fillers(self, text: str) -> Dict[str, int]:
        text_lower = text.lower()
        counts = {}
        for filler in self.FILLER_WORDS:
            count = len(re.findall(rf'\b{re.escape(filler)}\b', text_lower))
            if count > 0:
                counts[filler] = count
        return counts
    
    def calculate_wpm(self, word_count: int, duration_seconds: float) -> float:
        if duration_seconds <= 0:
            return 0
        return (word_count / duration_seconds) * 60
    
    def analyze(self, transcript: str, words_with_timestamps: List[Dict], duration_seconds: float) -> CommunicationFeedback:
        word_count = len(words_with_timestamps)
        wpm = self.calculate_wpm(word_count, duration_seconds)
        
        # Local filler count (independent of API)
        filler_count = self.count_fillers(transcript)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cheaper, faster, good enough for this
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Transcript ({word_count} words, ~{wpm:.0f} WPM):\n\n{transcript}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.4,
                max_tokens=800
            )
            #added
            result = json.loads(response.choices[0].message.content)
            
            return CommunicationFeedback(
                clarity_score=min(10, max(1, int(result.get("clarity_score", 5)))),
                structure_score=min(10, max(1, int(result.get("structure_score", 5)))),
                filler_count=filler_count,
                suggestions=result.get("suggestions", ["Practice more"])[:3],
                rewritten_version=result.get("rewritten_version", "No rewrite generated"),
                wpm=wpm
            )
            
        except Exception as e:
            print(f"API Error: {e}")
            # Fallback if API fails
            return CommunicationFeedback(
                clarity_score=5,
                structure_score=5,
                filler_count=filler_count,
                suggestions=["API error - check your key", "Practice speaking slower", "Record again"],
                rewritten_version="Error analyzing. Please try again.",
                wpm=wpm
            )