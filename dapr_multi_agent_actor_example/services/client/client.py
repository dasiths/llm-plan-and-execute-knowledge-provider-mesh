import requests
import time
import sys

if __name__ == "__main__":
    workflow_url = "http://localhost:8004/RunWorkflow"
    task_payload = {"task": "Find information about the Ryobi One Plus 18V Drill and check which stores have it in stock."}

    attempt = 1

    while attempt <= 2:
        try:
            print(f"Attempt {attempt}...")
            response = requests.post(workflow_url, json=task_payload, timeout=5)

            if response.status_code == 202:
                print("Workflow started successfully!")
                sys.exit(0)
            else:
                print(f"Received status code {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

        attempt += 1
        print(f"Waiting 1s seconds before next attempt...")
        time.sleep(1)

    print(f"Maximum attempts (10) reached without success.")

    print("Failed to get successful response")
    sys.exit(1)
