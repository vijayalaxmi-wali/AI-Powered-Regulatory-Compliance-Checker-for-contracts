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
    # Call scraping function every night at 12 AM
    schedule.every().day.at("00:00").do(scraping2.call_scrape_funtion)

    # For testing
    # schedule.every(10).seconds.do(scraping.call_scrape_funtion)
    # schedule.every(1).minutes.do(scraping.call_scrape_funtion)

    while True:
        schedule.run_pending()
        time.sleep(1)  # check every second

# Start scheduler in background thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    AGREEMENT_JSON_MAP = {
        "Data Processing Agreement": "json_files\dpa_sum.json",
        "Joint Controller Agreement": "json_files\jca_sum.json",
        "Controller-to-Controller Agreement": "json_files\c2c_sum.json",
        "Processor-to-Subprocessor Agreement": "json_files\sub_sum.json",
        "Standard Contractual Clauses": "json_files\scc_sum.json"
    }

    st.title("Contract Compliance Checker")

    uploaded_file = st.file_uploader("Upload an agreement (PDF Only)", type=["pdf"])

    if uploaded_file is not None:
        with open("temp_uploded.pdf", "wb") as f:
            f.write(uploaded_file.read())

        st.info("Processing your file....")

        try:
            # Step 1: Identify the type of agreement
            agreement_type = agreement_comparison.document_type("temp_uploded.pdf")
            st.write("**Detected Document Type:** ", agreement_type)

            if agreement_type in AGREEMENT_JSON_MAP:
                # Step 2: Extract clauses
                unseen_data = data_extraction.Clause_extraction("temp_uploded.pdf")
                st.write("**Clause Extraction Completed**")

                # ✅ Optional email for extraction success
                send_email_notification(
                    "✅ Clause Extraction Completed",
                    f"Document: temp_uploded.pdf\nType: {agreement_type}\nClause extraction done successfully."
                )

                # Step 3: Load template JSON
                template_file = AGREEMENT_JSON_MAP[agreement_type]
                with open(template_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)

                # Step 4: Compare agreements
                result = agreement_comparison.compare_agreements(unseen_data, template_data)

                # Show result
                st.subheader("Comparison Result")
                st.write(result)

                # ✅ Email only for comparison results
                send_email_notification(
                    "📊 Comparison Completed",
                    f"Document: temp_uploded.pdf\nType: {agreement_type}\nComparison result:\n{result}"
                )

            else:
                st.error("This document is not under GDPR Compliance")

                # ✅ Email only for unsupported doc
                send_email_notification(
                    "⚠️ Unsupported Document",
                    f"Document: temp_uploded.pdf\nDetected type: {agreement_type} is not supported."
                )
                
                

        except Exception as e:
            st.error(f"Error occurred: {e}")

            # ✅ Send errors only to Slack
            send_slack_notification(f"❌ Error in main Streamlit app: {str(e)}")
