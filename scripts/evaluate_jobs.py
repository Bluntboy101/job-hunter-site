import os
import json
import argparse
from datetime import datetime

def parse_jobs(jobs_file):
    if not os.path.exists(jobs_file):
        print(f"[ERROR] [evaluator] Jobs file {jobs_file} not found.")
        return []
    with open(jobs_file, 'r') as f:
        return json.load(f)

def evaluate_jobs(jobs, cv_path, needs):
    """
    Evaluates jobs using Google AI Studio MCP context.
    For this script to work autonomously, it must either invoke the MCP client directly 
    or rely on the agentic orchestration to inject the evaluation. 
    Here we format the prompt for the agent to run, or we could use the python google-genai SDK 
    if an API key is present. Let's use the google-genai SDK directly.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] [evaluator] Missing GEMINI_API_KEY environment variable.")
        return []

    print("[INFO] [evaluator] Reading CV to evaluate jobs...")
    cv_content = ""
    try:
        with open(cv_path, 'r') as f:
            cv_content = f.read()
    except Exception as e:
        print(f"[ERROR] [evaluator] Could not read CV: {e}")
        return []

    needs_content = needs
    if os.path.exists(needs):
        try:
            with open(needs, 'r') as f:
                needs_content = f.read()
                print("[INFO] [evaluator] Read specific needs from file.")
        except Exception as e:
            print(f"[WARNING] [evaluator] Could not read needs file: {e}")

    evaluated_jobs = []
    
    import urllib.request
    import urllib.error
    import time
    
    for idx, job in enumerate(jobs):
        # Respect Gemini free tier limit (15 RPM)
        if idx > 0:
            time.sleep(6)

        title = job.get('job_title') or 'Unknown Title'
        company = job.get('employer_name') or 'Unknown Company'
        desc = job.get('job_description') or ''
        url = job.get('job_apply_link') or ''
        
        prompt = f"""
        Evaluate this job against my CV and specific needs.
        
        My Needs:
        {needs_content}
        
        Job Title: {title}
        Company: {company}
        Job Description: {desc[:3000]} # Truncated for token limit
        
        My CV:
        {cv_content[:4000]}
        
        Based on my CV and needs, output a JSON array containing EXACTLY ONE object with these exact keys:
        - "fit_score": an integer from 1 to 100 rating how well this job matches my CV and needs.
        - "reasoning": a short 1-2 sentence explanation of why.
        """
        
        payload_data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }
        
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    gemini_url,
                    data=json.dumps(payload_data).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req) as response:
                    if response.status == 200:
                        resp_json = json.loads(response.read().decode('utf-8'))
                        text_resp = resp_json['candidates'][0]['content']['parts'][0]['text']

                        try:
                            eval_data_list = json.loads(text_resp)
                            if isinstance(eval_data_list, list) and len(eval_data_list) > 0:
                                eval_data = eval_data_list[0]
                            else:
                                eval_data = eval_data_list

                            job['fit_score'] = eval_data.get('fit_score', 0)
                            job['evaluation_reason'] = eval_data.get('reasoning', 'No reasoning provided.')
                            evaluated_jobs.append(job)
                            print(f"[INFO] [evaluator] Evaluated {title} at {company} - Score: {job['fit_score']}")
                        except json.JSONDecodeError:
                            print(f"[WARNING] [evaluator] Could not parse AI response JSON for job {idx}")
                    else:
                        print(f"[ERROR] [evaluator] Gemini API error: {response.status}")
                break  # Success, no retry needed
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 2:
                    wait = 30 * (attempt + 1)
                    print(f"[WARNING] [evaluator] Rate limited on job {idx}, waiting {wait}s (attempt {attempt + 1}/3)")
                    time.sleep(wait)
                else:
                    print(f"[ERROR] [evaluator] AI evaluation failed for job {idx}: {e}")
                    break
            except Exception as e:
                print(f"[ERROR] [evaluator] AI evaluation failed for job {idx}: {e}")
                break
            
    # Sort by fit_score descending
    evaluated_jobs.sort(key=lambda x: x.get('fit_score', 0), reverse=True)
    return evaluated_jobs

def main():
    parser = argparse.ArgumentParser(description="Evaluate job listings against CV.")
    parser.add_argument("--jobs", type=str, default=".tmp/raw_jobs.json", help="Input jobs file")
    parser.add_argument("--cv", type=str, required=True, help="Path to CV file")
    parser.add_argument("--needs", type=str, default="None specified", help="User specific needs")
    parser.add_argument("--output", type=str, default=".tmp/evaluated_jobs.json", help="Output file")
    
    args = parser.parse_args()
    
    start_time = datetime.now()
    print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] [evaluator] Starting evaluation")
    
    jobs = parse_jobs(args.jobs)
    if not jobs:
        return
        
    evaluated_jobs = evaluate_jobs(jobs, args.cv, args.needs)
    
    with open(args.output, 'w') as f:
        json.dump(evaluated_jobs, f, indent=2)
        
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] [SUCCESS] [evaluator] Evaluated {len(evaluated_jobs)} jobs in {duration:.1f}s")

if __name__ == "__main__":
    main()
