# gemini_filter.py
"""
Gemini AI-powered job relevance filter.
Uses Google's Gemini API to intelligently evaluate job fit for the candidate.
"""

import os
import google.generativeai as genai
import time

# Candidate Profile - Comprehensive background for Gemini to reference
CANDIDATE_PROFILE = """
# TIFFANY M. CHAO - Candidate Profile

## SUMMARY
Strategic and creative Public Relations leader with 8+ years of experience driving high-impact campaigns 
across entertainment, media, and brand communications. Known for innovative storytelling and strong media 
relationships. Recognized as "Rising Star in PR" by Business Insider and "15 Under 35" by PRSA.

## CORE EXPERTISE
- **Entertainment PR/Publicity**: Paramount, Nickelodeon, studio campaigns
- **Celebrity & Talent Publicity**: Reality TV stars, musicians, influencers
- **Music Industry PR**: Republic Records background, artist publicity
- **Event PR**: Awards shows, premieres, red carpets, launches
- **Tentpole Campaigns**: Super Bowl (8.5B impressions), Kids' Choice Awards (7B), NFL Wild Card (6.5B)

## WORK HISTORY
- **Publicity Manager** at Paramount/Nickelodeon (2022-2025) - Los Angeles
  - Led campaigns for live-action series, movies, and tentpole events
  - Managed talent relations for Comic-Con, press tours, and premieres
  - Sports Emmy Award-winning Super Bowl LVIII campaign
  
- **Senior Publicist** at Paramount/Nickelodeon (2021-2022) - New York
  - Managed publicity for Kids & Family channels and platforms
  - Led NFL Wild Card on Nickelodeon campaign (6.5B impressions)
  
- **Freelance Celebrity Publicist** - Current
  - Giannina Gibelli (Love Is Blind) - Reality TV talent publicity
  - Brooklyn Chop House - Restaurant launch PR and events
  - Musicians and entertainment clients

- **Republic Records** - Publicity temp (music industry experience)
- **Production Experience**: GRAMMYs, NBA Awards, Black Girls Rock (script PA/coordinator)

## TARGET ROLES (What She's Looking For)
- Level: Manager, Senior Manager, Director
- Functions: PR, Publicity, Communications, Media Relations
- Industries: Entertainment, Media, Music, Streaming, Television, Film
- Location: Los Angeles area (hybrid) or Remote
- NOT looking for: Junior roles, tech/engineering, performance marketing, sales

## KEY SKILLS & ACHIEVEMENTS
- Press campaign strategy and execution
- Talent/celebrity media relations
- Stakeholder management (studios, agencies, talent)
- Award show publicity and event PR
- Press releases, talking points, media materials
- National and trade media pitching
- Team leadership and coordination
"""

class GeminiJobFilter:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found. AI filtering disabled.")
            self.enabled = False
            return
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.enabled = True
        self.rate_limit_delay = 1.0  # Seconds between API calls to avoid rate limits
        
    def evaluate_job(self, job_title: str, company: str, job_description: str, location: str = "") -> dict:
        """
        Evaluates a job posting against the candidate profile using Gemini.
        
        Returns:
            dict with keys:
            - score (int): 1-10 relevance score
            - recommendation (str): "SEND", "MAYBE", or "SKIP"
            - reasoning (str): Brief explanation
            - highlights (list): Key matching points
        """
        if not self.enabled:
            # Fallback: pass everything through if Gemini not available
            return {
                "score": 5,
                "recommendation": "MAYBE",
                "reasoning": "AI filter unavailable - manual review recommended",
                "highlights": [],
                "requirements": []
            }
        
        prompt = f"""You are a recruiting assistant evaluating job fit for a specific candidate.

## CANDIDATE PROFILE:
{CANDIDATE_PROFILE}

## JOB POSTING TO EVALUATE:
**Title:** {job_title}
**Company:** {company}
**Location:** {location}
**Description:** 
{job_description[:3000]}  

## YOUR TASK:
Evaluate how well this job matches the candidate's background, skills, and career goals.

Consider:
1. Does the role match her experience level (8+ years, Manager/Director level)?
2. Is it in her target industries (entertainment, media, music, streaming)?
3. Does it align with her core skills (PR, publicity, communications, media relations)?
4. Is the location compatible (LA area or remote)?
5. Are there any red flags (too junior, wrong field, technical role)?

## RESPONSE FORMAT (JSON only, no markdown):
{{
    "score": <1-10 integer>,
    "recommendation": "<SEND|MAYBE|SKIP>",
    "reasoning": "<2-3 sentence explanation of why this is/isn't a good match>",
    "highlights": ["<matching point 1>", "<matching point 2>"],
    "requirements": ["<key requirement 1>", "<key requirement 2>", "<key requirement 3>"]
}}

Note: "requirements" should list 2-4 key job requirements/qualifications from the posting.

SCORING GUIDE:
- 9-10: Perfect match - exactly her target role/industry
- 7-8: Strong match - relevant role, good fit
- 5-6: Possible match - adjacent role, worth considering
- 3-4: Weak match - tangentially related
- 1-2: Poor match - wrong level, industry, or function

RECOMMENDATION GUIDE:
- SEND: Score 7+ (automatically send to candidate)
- MAYBE: Score 5-6 (send with caveat)
- SKIP: Score 4 or below (don't bother candidate)

Respond with ONLY the JSON object, no other text."""

        try:
            time.sleep(self.rate_limit_delay)  # Rate limiting
            response = self.model.generate_content(prompt)
            
            # Parse the response
            response_text = response.text.strip()
            
            # Clean up response if it has markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            import json
            result = json.loads(response_text)
            
            # Validate and normalize
            result["score"] = max(1, min(10, int(result.get("score", 5))))
            result["recommendation"] = result.get("recommendation", "MAYBE").upper()
            result["reasoning"] = result.get("reasoning", "No reasoning provided")
            result["highlights"] = result.get("highlights", [])
            result["requirements"] = result.get("requirements", [])
            
            return result
            
        except Exception as e:
            print(f"  [GEMINI ERROR] {e}")
            # On error, be permissive - let the job through for manual review
            return {
                "score": 5,
                "recommendation": "MAYBE",
                "reasoning": f"AI evaluation failed: {str(e)[:50]}",
                "highlights": [],
                "requirements": []
            }
    
    def batch_evaluate(self, jobs: list) -> list:
        """
        Evaluates a batch of jobs and returns only those worth sending.
        
        Args:
            jobs: List of job dicts with keys: title, company, url, description, location
            
        Returns:
            List of jobs that passed the filter, with AI scores added
        """
        if not self.enabled:
            print("  [INFO] Gemini filter disabled - passing all jobs through")
            return jobs
            
        print(f"\n🤖 Gemini AI Evaluation: Analyzing {len(jobs)} candidate jobs...")
        
        filtered_jobs = []
        
        for i, job in enumerate(jobs):
            title = job.get("title", "Unknown")
            company = job.get("company", "Unknown")
            description = job.get("description", job.get("title", ""))
            location = job.get("location", "Unknown")
            
            print(f"  [{i+1}/{len(jobs)}] Evaluating: {title} @ {company}...", end=" ")
            
            result = self.evaluate_job(title, company, description, location)
            
            # Add AI evaluation to job
            job["ai_score"] = result["score"]
            job["ai_recommendation"] = result["recommendation"]
            job["ai_reasoning"] = result["reasoning"]
            job["ai_highlights"] = result["highlights"]
            job["ai_requirements"] = result["requirements"]
            
            print(f"Score: {result['score']}/10 → {result['recommendation']}")
            
            # Filter based on recommendation
            if result["recommendation"] in ["SEND", "MAYBE"]:
                filtered_jobs.append(job)
            else:
                print(f"    └─ Skipped: {result['reasoning'][:60]}...")
        
        print(f"\n✅ AI Filter Results: {len(filtered_jobs)}/{len(jobs)} jobs passed")
        return filtered_jobs

    def filter_jobs(self, jobs: list, min_score: int = 7) -> list:
        """
        Main entry point for filtering jobs. Evaluates all jobs and returns
        only those meeting the minimum score threshold.
        
        Args:
            jobs: List of job dicts with keys: title, company, url, description, location
            min_score: Minimum AI score (1-10) required to pass filter (default: 7)
            
        Returns:
            List of jobs that passed the filter with AI metadata attached
        """
        if not self.enabled:
            print("  [INFO] Gemini filter disabled - passing all jobs through")
            return jobs
        
        if not jobs:
            print("  [INFO] No jobs to evaluate")
            return []
        
        print(f"\n🤖 Gemini AI Evaluation: Analyzing {len(jobs)} jobs (min_score: {min_score})...")
        
        filtered_jobs = []
        
        for i, job in enumerate(jobs):
            title = job.get("title", "Unknown")
            company = job.get("company", "Unknown")
            description = job.get("description", job.get("title", ""))
            location = job.get("location", "Unknown")
            
            print(f"  [{i+1}/{len(jobs)}] {title} @ {company}...", end=" ")
            
            result = self.evaluate_job(title, company, description, location)
            
            # Attach AI evaluation metadata to job
            job["ai_score"] = result["score"]
            job["ai_recommendation"] = result["recommendation"]
            job["ai_reasoning"] = result["reasoning"]
            job["ai_highlights"] = result["highlights"]
            job["ai_requirements"] = result["requirements"]
            
            # Check against minimum score threshold
            if result["score"] >= min_score:
                print(f"✓ {result['score']}/10")
                filtered_jobs.append(job)
            else:
                print(f"✗ {result['score']}/10 - {result['reasoning'][:50]}...")
        
        # Summary
        print(f"\n📊 AI Filter Summary:")
        print(f"   • Total evaluated: {len(jobs)}")
        print(f"   • Passed (score ≥ {min_score}): {len(filtered_jobs)}")
        print(f"   • Rejected: {len(jobs) - len(filtered_jobs)}")
        
        return filtered_jobs


# For testing
if __name__ == "__main__":
    filter = GeminiJobFilter()
    
    # Test job
    test_job = {
        "title": "Senior Publicist, Entertainment",
        "company": "Netflix",
        "description": """
        Netflix is looking for a Senior Publicist to join our Entertainment PR team.
        You will lead publicity campaigns for original series and films, manage talent
        relations, and work with internal teams on strategic communications.
        
        Requirements:
        - 6+ years in entertainment publicity or related field
        - Experience with talent media training and press tours
        - Strong relationships with entertainment press
        - Based in Los Angeles (hybrid)
        """,
        "location": "Los Angeles, CA"
    }
    
    result = filter.evaluate_job(
        test_job["title"],
        test_job["company"], 
        test_job["description"],
        test_job["location"]
    )
    
    print("\nTest Result:")
    print(f"  Score: {result['score']}/10")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Reasoning: {result['reasoning']}")
    print(f"  Highlights: {result['highlights']}")
