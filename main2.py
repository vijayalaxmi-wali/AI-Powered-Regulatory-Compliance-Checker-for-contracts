import agreement_comparison
import data_extraction
import json
import streamlit as st 
import schedule
import threading
import time
import scraping2

# ✅ Import individual notification functions
from notification import send_email_notification, send_slack_notification

def run_scheduler():
    
    # call call_scrape_funtion function every night at 12 am 
    schedule.every().day.at("00:00").do(scraping2.call_scrape_funtion)
    
    # these are for testing purpose 
    # schedule.every(10).seconds.do(scraping.call_scrape_funtion)
    # schedule.every(1).minutes.do(scraping.call_scrape_funtion)
    
    while True:
        schedule.run_pending()
        time.sleep(1)     #check every 5 seconds 

# start scheduler in background thread so streamlit does not block 
threading.Thread(target=run_scheduler, daemon=True).start() 

if __name__ == "__main__":
    
    AGREEMENT_JSON_MAP={
        "Data Processing Agreement":"json_files\dpa_sum.json",
        "Joint Controller Agreement": "json_files\jca_sum.json",
        "Controller-to-Controller Agreement":"json_files\c2c_sum.json",
        "Processor-to-Subprocessor Agreement":"json_files\sub_sum.json",
        "Standard Contractual Clauses": "json_files\scc_sum.json"
    }
    
    st.title("Contract Compliance Checker")
    
    # file upload 
    uploaded_file = st.file_uploader("Upload an agreement (PDF Only)", type=["pdf"] )
    
    if uploaded_file is not None:
        with open("temp_uploded.pdf", "wb") as f:
            f.write(uploaded_file.read())
            
            st.info("Processing your file....")
            
            # step 1: identify the type of agreement
            agreement_type = agreement_comparison.document_type("temp_uploded.pdf")
            
            st.write("**Detected Document Type:** ", agreement_type)
            
            if agreement_type in AGREEMENT_JSON_MAP:
                
                # step 2 : extract clause from unseen file 
                unseen_data = data_extraction.Clause_extraction("temp_uploded.pdf")
                
                st.write("**Clause Extraction Completed**")
                
                # ✅ Notification after clause extraction
                subject = "✅ Clause Extraction Completed"
                message = f"Document: temp_uploded.pdf\nType: {agreement_type}\nClause extraction done successfully."

                send_email_notification(subject, message)
                send_slack_notification(f"*{subject}*\n{message}")
                
                # step 3: Load respective templete json 
                template_file = AGREEMENT_JSON_MAP[agreement_type]
                
                print("template_file------------", template_file)
                
                with open(template_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)
                    
                # step 4: Compare agreements
                result = agreement_comparison.compare_agreements(unseen_data, template_data)
                
                # show result
                st.subheader("Comparison Result")
                st.write(result)
                
                # ✅ Notification after comparison
                subject = "📊 Comparison Completed"
                message = f"Document: temp_uploded.pdf\nType: {agreement_type}\nComparison result: {result}"

                send_email_notification(subject, message)
                send_slack_notification(f"*{subject}*\n{message}")
            else:
                st.error(f"This document is not under GDPR Complience")   

                # ✅ Notification for unsupported document
                subject = "⚠️ Unsupported Document"
                message = f"Document: temp_uploded.pdf\nDetected type: {agreement_type} is not supported."

                send_email_notification(subject, message)
                send_slack_notification(f"*{subject}*\n{message}")
