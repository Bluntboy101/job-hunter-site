import os
import json
import argparse
from datetime import datetime

def generate_report(evaluated_jobs_file, output_file, history_file):
    if not os.path.exists(evaluated_jobs_file):
        print(f"[ERROR] [reporter] Evaluated jobs file {evaluated_jobs_file} not found.")
        return
        
    with open(evaluated_jobs_file, 'r') as f:
        new_jobs = json.load(f)
        
    # Load historical jobs
    historical_jobs = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                historical_jobs = json.load(f)
        except Exception as e:
            print(f"[WARNING] [reporter] Could not load history: {e}")

    # Merge and deduplicate using job_id or apply link
    all_jobs_dict = {}
    for job in historical_jobs:
        job_key = job.get('job_id') or job.get('job_apply_link') or (job.get('job_title', '') + job.get('employer_name', ''))
        all_jobs_dict[job_key] = job
        
    for job in new_jobs:
        job_key = job.get('job_id') or job.get('job_apply_link') or (job.get('job_title', '') + job.get('employer_name', ''))
        all_jobs_dict[job_key] = job

    # Sort combined jobs by fit_score descending
    combined_jobs = list(all_jobs_dict.values())
    combined_jobs.sort(key=lambda x: x.get('fit_score', 0), reverse=True)
    
    # Save back to history
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    with open(history_file, 'w') as f:
        json.dump(combined_jobs, f, indent=2)

    today = datetime.now().strftime('%Y-%m-%d')
    md_content = f"# Job Hunter Multi-Day Report - {today}\n\n"
    md_content += f"Currently tracking **{len(combined_jobs)}** unique jobs based on your CV and needs. Ranked by best fit.\n\n"
    
    md_content += "## Top Matches\n\n"
    
    count = 0
    for idx, job in enumerate(combined_jobs):
        score = job.get('fit_score', 0)
        # Show only somewhat relevant jobs (score > 20) or just the top 50 overall
        if score < 20: 
            continue
            
        count += 1
        if count > 50: # Max 50 items displayed in the markdown report
            break
            
        title = job.get('job_title', 'Unknown Title')
        company = job.get('employer_name', 'Unknown Company')
        reason = job.get('evaluation_reason', '')
        link = job.get('job_apply_link', '#')
        city = job.get('job_city') or ''
        state = job.get('job_state') or ''
        location = f"{city}, {state}".strip(", ")
        if not location:
            location = "Remote / Unspecified"
        
        md_content += f"### {count}. {title} at {company} (Score: {score}/100)\n"
        md_content += f"- **Location**: {location}\n"
        md_content += f"- **Why it's a fit**: {reason}\n"
        md_content += f"- **[Apply Here]({link})**\n\n"
        
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(md_content)
        
    print(f"[SUCCESS] [reporter] Report generated at {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate markdown report from evaluated jobs.")
    parser.add_argument("--input", type=str, default=".tmp/evaluated_jobs.json", help="Evaluated jobs JSON")
    parser.add_argument("--output", type=str, default="deliverables/job_report.md", help="Output markdown file")
    parser.add_argument("--history", type=str, default="deliverables/historical_jobs.json", help="Historical jobs JSON")
    
    args = parser.parse_args()
    
    start_time = datetime.now()
    print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] [reporter] Generating cumulative report")
    
    generate_report(args.input, args.output, args.history)

if __name__ == "__main__":
    main()
