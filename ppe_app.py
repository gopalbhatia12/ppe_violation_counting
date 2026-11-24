import os
import tempfile

import streamlit as st

from email_alert import send_report_email
from report_generator import generator
from video_processor import process_video


st.set_page_config(
    page_title="PPE Detection System",
    page_icon="🦺",
    layout="wide"
)

st.title("PPE Violation Detection and People Counting")

st.write(
    "Upload a video to detect people, check helmet and "
    "safety vest status, and estimate people counts."
)

uploaded_file = st.file_uploader(
    "Upload a video",
    type=["mp4", "avi", "mov", "mkv"]
)

if uploaded_file is not None:
    st.markdown("""
        <style>
        video {
        max-height : 450px !important
        width : 500px
        }
        </style>
    """, unsafe_allow_html=True)
    st.video(uploaded_file, width=500)

    upload_key = (uploaded_file.name, uploaded_file.size)
    if st.session_state.get("upload_key") != upload_key:
        st.session_state.upload_key = upload_key
        st.session_state.pop("processed_result", None)

    if st.button("Start Detection"):
        os.makedirs("outputs", exist_ok=True)
        input_temp = None

        try:
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            ) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                input_temp = temp_file.name

            output_path = os.path.abspath(
                "outputs/annotated_video.mp4"
            )
            csv_path = os.path.abspath(
                "outputs/ppe_report.csv"
            )

            with st.spinner("Processing video..."):
                dataframe, metrics = process_video(
                    input_temp,
                    output_path
                )
                summary = generator(dataframe, csv_path)

            st.session_state.processed_result = {
                "dataframe": dataframe,
                "metrics": metrics,
                "summary": summary,
                "output_path": output_path,
                "csv_path": csv_path,
                "video_name": uploaded_file.name,
            }
        except Exception as error:
            st.session_state.pop("processed_result", None)
            st.error(f"An error occurred: {error}")
        finally:
            if input_temp and os.path.exists(input_temp):
                os.remove(input_temp)

    result = st.session_state.get("processed_result")
    if result is not None:
        dataframe = result["dataframe"]
        metrics = result["metrics"]
        summary = result["summary"]
        output_path = result["output_path"]
        csv_path = result["csv_path"]

        st.success("Video processing completed!")

        st.subheader("People Counting Results")
        col1, col2, col3 = st.columns(3)
        col1.metric("Unique tracked IDs", metrics["unique_tracked_ids"])
        col2.metric(
            "Maximum people in one frame",
            metrics["maximum_people_in_frame"]
        )
        col3.metric("Frames processed", metrics["processed_frames"])

        st.subheader("PPE Results")
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Violation observations",
            summary["violation_observations"]
        )
        col2.metric(
            "Safe observations",
            summary["compliant_observations"]
        )
        col3.metric("Needs review", summary["review_observations"])

        st.subheader("Detection Report")
        st.dataframe(dataframe, use_container_width=True)

        st.subheader("Email Report")
        st.write("Send the processed PPE report to your email.")
        receiver_email = st.text_input(
            "Enter recipient email address",
            placeholder="example@gmail.com"
        )

        if st.button("Send Report via Email"):
            if not receiver_email or "@" not in receiver_email:
                st.warning("Please enter a valid email address.")
            else:
                try:
                    send_report_email(
                        receiver_email=receiver_email,
                        video_name=result["video_name"],
                        report_df=dataframe
                    )
                    st.success("PPE report sent successfully!")
                except Exception as error:
                    st.error(f"Email sending failed: {error}")

        st.subheader("Processed Video")
        with open(output_path, "rb") as video_file:
            st.video(video_file.read(), width=500)

        with open(output_path, "rb") as video_file:
            st.download_button(
                "Download Annotated Video",
                data=video_file,
                file_name="annotated_video.mp4",
                mime="video/mp4"
            )

        with open(csv_path, "rb") as csv_file:
            st.download_button(
                "Download CSV Report",
                data=csv_file,
                file_name="ppe_report.csv",
                mime="text/csv"
            )
