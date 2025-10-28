import requests, json
import data_extraction
import time

# ✅ Import individual notification functions
from notification import send_email_notification, send_slack_notification

# scrape data from different link using get api 
def scrape_data(url, name):
    try:
        response = requests.get(url, stream=True)
        if response.status_code==200:
            with open(name, "wb") as f:
                for chunck in response.iter_content(chunk_size=1024):
                    if chunck:
                        f.write(chunck)
            print("Download Successful", time.ctime())
            
            # ✅ Notification after download
            subject = "✅ Download Completed"
            message = f"File: {name}\nURL: {url}\nTime: {time.ctime()}"

            send_email_notification(subject, message)
            send_slack_notification(f"*{subject}*\n{message}")

        else:
            print("failed to download", response.status_code)

            # ✅ Notification if download fails
            subject = "⚠️ Download Failed"
            message = f"File: {name}\nURL: {url}\nStatus code: {response.status_code}"

            send_email_notification(subject, message)
            send_slack_notification(f"*{subject}*\n{message}")

    except Exception as e:
        print("Error during download:", e)

        # ✅ Notification for download error
        subject = "⚠️ Error in Download"
        message = f"File: {name}\nURL: {url}\nError: {e}"

        send_email_notification(subject, message)
        send_slack_notification(f"*{subject}*\n{message}")
    
    
def call_scrape_funtion():
    
    DOCUMENT_MAP= {
        "DPA": {"json_file":"json_files\dpa_sum.json", "link":r"https://www.benchmarkone.com/wp-content/uploads/2018/05/GDPR-Sample-Agreement.pdf"},
        "JCA": {"json_file":"json_files\jca_sum.json", "link":r"https://www.surf.nl/files/2019-11/model-joint-controllership-agreement.pdf"},
        "C2C":{"json_file":"json_files\c2c_sum.json", "link":r"https://www.fcmtravel.com/sites/default/files/2020-03/2-Controller-to-controller-data-privacy-addendum.pdf"},    
        "SCC":{"json_file":"json_files\scc_sum.json", "link":r"https://www.miller-insurance.com/assets/PDF-Downloads/Standard-Contractual-Clauses-SCCs.pdf"},    
        "subprocessing":{"json_file":"json_files\sub_sum.json", "link":r"https://greaterthan.eu/wp-content/uploads/Personal-Data-Sub-Processor-Agreement-2024-01-24.pdf"}    
    }
    
    temp_agreement= "temp_agreement.pdf"
    
    for key, value in DOCUMENT_MAP.items():
        # dealing with DPA agreement only
        scrape_data(DOCUMENT_MAP[key]["link"], temp_agreement)
        
        clauses = data_extraction.Clause_extraction(temp_agreement)
        
        # Step 6: Update respective json file with new clauses (dpa.json)
        with open(DOCUMENT_MAP[key]["json_file"], "w", encoding="utf-8") as f:
            json.dump(clauses, f, indent=2, ensure_ascii=False)

        # ✅ Notification after JSON update
        subject = "📄 JSON Updated"
        message = f"File: {DOCUMENT_MAP[key]['json_file']} updated successfully with new clauses."

        send_email_notification(subject, message)
        send_slack_notification(f"*{subject}*\n{message}")
    
# call_scrape_funtion()
