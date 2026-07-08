import json
from groq import Groq
from app.core.config import GROQ_API_KEY
from app.schemas.analysis import JobAnalysis

client = Groq(api_key=GROQ_API_KEY)

ANALYSIS_PROMPT = """You are analyzing a job description. Return ONLY valid JSON, no other text, matching exactly this shape:

{
  "required_skills": ["skill1", "skill2"],
  "seniority_level": "entry|mid|senior",
  "years_experience_required": "e.g. 2-4 years, or null if not mentioned",
  "key_responsibilities": ["responsibility1", "responsibility2"],
  "red_flags": ["any concerning phrases like unpaid overtime, wears many hats, etc, or empty list if none"]
}

Job description:
"""

def analyze_job_description(job_description: str) -> JobAnalysis | None:
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": ANALYSIS_PROMPT + job_description}
            ],
            temperature=0.2,
        )
        raw_text = response.choices[0].message.content.strip()

        raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        data = json.loads(raw_text)
        return JobAnalysis(**data)

    except Exception as e:
        print(f"AI analysis failed: {e}")
        return None