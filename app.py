import streamlit as st
import os
from PIL import Image 
import google.generativeai as genai
from layouts import get_gemini_response,input_pdf_setup
from prompts import generate_profile_json, generate_matching_json, generate_final_thoughts, generate_missing_skills, generate_resources
import base64
import json
import pandas as pd
import tempfile
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def main():
    st.set_page_config(layout="wide",page_title="Prospect CV",page_icon=":rocket:",initial_sidebar_state="expanded")
    st.markdown(
        """
            <style>
                .appview-container .main .block-container {{
                    padding-top: {padding_top}rem;
                    padding-bottom: {padding_bottom}rem;
                    }}

            </style>""".format(
            padding_top=1, padding_bottom=1
        ),
        unsafe_allow_html=True,
    )
    profile_json = {}
    match_parameters = {}
    final_thoughts = ""
    skills = {}
    resources = ""
    submitted = False
    st.title("Prospect CV")
    tab1, tab2, tab3, tab4 = st.tabs(["Profile Information", "Resume Analysis", "Improvements", "Resources"])
    with st.sidebar:
        uploaded_file = st.file_uploader(
            "Upload your Resume (PDF) and Click on the Submit", type=["pdf"])
        job_description_text = st.text_area("Input Job Description, Leave Blank if not required")
        if st.button("Submit and Process"):
            with st.spinner("Processing..."):
                if uploaded_file is not None and job_description_text != "":
                    file_path = save_uploaded_file(uploaded_file)
                    profile_json,match_parameters,final_thoughts, skills, resources = process_file(file_path, job_description_text)
                    submitted = True
                    st.success("Resume and JD Processed Successfully")
                elif uploaded_file is None:
                    st.error("Please upload the resume")
                elif job_description_text == "":
                    file_path = save_uploaded_file(uploaded_file)
                    profile_json,match_parameters,final_thoughts = process_file(file_path, None)
                    submitted = True
                    st.success("Resume Processed Successfully")

    with tab1:
        left_column, right_column = st.columns(2)
        with left_column:
            st.subheader("Profile Information:")
            if uploaded_file is not None and submitted:
                display_profile_data(profile_json)
            else:
                st.write("Please upload the resume and press Submit")
        with right_column:
            st.subheader("Resume:")
            if uploaded_file is not None:
                displayPDF(uploaded_file, 600)
            else:
                st.write("Please upload the resume")

    with tab2:
        if job_description_text == "":
            st.write("Please input a Job Description to get the Match Parameters")
        elif submitted == False:
            st.write("Please click on the Submit button to process the Resume")
        else:
            if match_parameters != {}:
                data = match_parameters

                matches_df = pd.DataFrame(data["explanations"]["matches"], index=range(len(data["explanations"]["matches"])))

                missing_df = pd.DataFrame(data["explanations"]["missing"],  index=range(len(data["explanations"]["missing"])))

                st.subheader(f"Match percentage: {data['match_percentage']}%")

                st.write("**Matches:**")
                st.table(matches_df)

                st.write("**Missing skills:**")
                st.table(missing_df)

                st.subheader("Final Thoughts:")
                st.write(final_thoughts)

    with tab3:
        #Highlight present and missing skills
        st.subheader("Improvements")
        if skills != {}:           
            present = skills.get("present", [])
            missing = skills.get("missing", [])
            left_column, right_column = st.columns(2)
            with right_column:
                st.write("Missing Skills:")
                st.table(pd.DataFrame(missing, columns=["Missing Skills"]))
            with left_column:
                st.write("Present Skills:")
                st.table(pd.DataFrame(present, columns=["Present Skills"]))

    
    with tab4:
        st.subheader("Resources")
        if resources != "":
            st.write(resources)


def display_profile_data(json_data):
    basics = json_data.get("basics", {})
    title = True
    basics_fields = ["Name", "Email", "Phone", "Website", "Experience"]
    basics_keys = ["name", "email", "phone", "website", "experienceInYears"]
    
    for field, key in zip(basics_fields, basics_keys):
        value = basics.get(key)
        if value:
            if title:
                st.subheader(f"Name: {value}")
                title = False
            else:
                st.write(f"{field}: {value}")

def displayPDF(upl_file, ui_width):
    bytes_data = upl_file.getvalue()
    base64_pdf = base64.b64encode(bytes_data).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width={str(ui_width)} height={str(ui_width*4/3)} type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def save_uploaded_file(uploaded_file):
    temp_dir = tempfile.mkdtemp()
    unique_id = str(hash(uploaded_file.name))
    file_path = os.path.join(temp_dir, unique_id)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def process_file(file_path, jd_text):
    profile_json = {}
    match_parameters = {}
    final_thoughts = ""
    skills = []
    resources = ""
    profile_json = generate_profile_json(file_path)
    if jd_text is not None:
        match_parameters = generate_matching_json(file_path, jd_text)
        final_thoughts = generate_final_thoughts(file_path, jd_text)
        skills = generate_missing_skills(file_path, jd_text)
        resources = generate_resources(file_path, jd_text)
    os.remove(file_path)
    return profile_json, match_parameters, final_thoughts, skills, resources

if __name__ == "__main__":
    main()

   





