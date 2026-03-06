import os
import json
import urllib.request
import urllib.parse
from datetime import datetime
import argparse

def scrape_jobs(query, location, num_pages=1):
    """
    Scrapes jobs using JSearch API (RapidAPI)
    Requires environment variable: RAPIDAPI_KEY
    """
    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        print("[ERROR] [scraper] Missing RAPIDAPI_KEY environment variable.")
        return []

    url_base = "https://jsearch.p.rapidapi.com/search"
    
    all_jobs = []
    
    print(f"[INFO] [scraper] Searching for: '{query}' in '{location}'")
    
    for page in range(1, num_pages + 1):
        params = {"query": f"{query} {location}", "page": str(page), "num_pages": "1"}
        query_string = urllib.parse.urlencode(params)
        url = f"{url_base}?{query_string}"
        
        req = urllib.request.Request(url, headers={
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        })
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    jobs = data.get('data', [])
                    all_jobs.extend(jobs)
                    print(f"[INFO] [scraper] Retrieved {len(jobs)} jobs from page {page}")
                else:
                    print(f"[ERROR] [scraper] API request failed with status: {response.status}")
                    break
        except Exception as e:
            print(f"[ERROR] [scraper] API request failed: {e}")
            break

    return all_jobs

def main():
    parser = argparse.ArgumentParser(description="Scrape job listings.")
    parser.add_argument("--query", type=str, required=True, help="Job title/keywords")
    parser.add_argument("--location", type=str, required=True, help="Location for jobs")
    parser.add_argument("--output", type=str, default=".tmp/raw_jobs.json", help="Output file")
    
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to fetch")
    
    args = parser.parse_args()
    
    start_time = datetime.now()
    print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] [scraper] Starting job scrape")
    
    jobs = scrape_jobs(args.query, args.location, num_pages=args.pages)
    
    # Save to tmp file
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(jobs, f, indent=2)
        
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] [SUCCESS] [scraper] Saved {len(jobs)} jobs to {args.output} in {duration:.1f}s")

if __name__ == "__main__":
    main()
