import os
import requests
import streamlit as st
import fitz  # PyMuPDF for PDFs
import docx
from bs4 import BeautifulSoup
from llama_cpp import Llama
from googlesearch import search

# Google Drive Direct Download Link for Model File
gguf_url = "https://drive.google.com/uc?export=download&id=1BMmP-W_Lq_LWbomxcbaYCVdcy4l54kvP"
model_path = "capybarahermes-2.5-mistral-7b.Q4_K_M.gguf"

# Function to download the model if not available
def download_model():
    if not os.path.exists(model_path):
        st.write("📥 Downloading AI model... This may take some time.")
        response = requests.get(gguf_url, stream=True)
        with open(model_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        st.write("✅ Download complete!")

# Download the model
download_model()

# Load AI Model
llm = Llama(model_path=model_path)

st.set_page_config(page_title="CyberDose Career Path AI", page_icon="🔒")
st.title("🔒 CyberDose Career Path AI")
st.write("AI-powered tool to explore Cyber Security careers and find job opportunities.")

# ========== FUNCTION TO EXTRACT TEXT FROM RESUME ==========
def extract_text_from_resume(uploaded_file):
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text("text") + "\n"
    elif uploaded_file.name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

# ========== AI-BASED RESUME OPTIMIZATION ==========
def optimize_resume(resume_text, job_desc):
    prompt = f"""
    Optimize the following resume to match the job description:
    --- Resume ---
    {resume_text}
    --- Job Description ---
    {job_desc}
    """
    return llm(prompt)['choices'][0]['text']

# ========== FUNCTION TO ANALYZE RESUME AND RECOMMEND JOBS ==========
def recommend_jobs_based_on_resume(resume_text):
    job_query = f"Cyber Security job matching {resume_text[:500]} site:linkedin.com OR site:indeed.com OR site:glassdoor.com"
    job_results = []
    for result in search(job_query, num_results=3):
        job_results.append(scrape_job_details(result))
    return job_results

# ========== FUNCTION TO SCRAPE JOB DETAILS ==========
def scrape_job_details(job_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(job_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        job_details = {
            "Job Role": soup.find("h1").text if soup.find("h1") else "Not Found",
            "Company": soup.find("a", class_="topcard__org-name-link").text if soup.find("a", class_="topcard__org-name-link") else "Not Found",
            "Location": soup.find("span", class_="topcard__flavor--bullet").text if soup.find("span", class_="topcard__flavor--bullet") else "Not Found",
            "Experience": "Not Found",
            "Salary": "Not Found",
            "Skills": "Not Found",
            "Apply Link": job_url
        }
        return job_details
    except Exception as e:
        return {"Error": str(e)}

# ========== JOB SEARCH UI ==========
st.subheader("🔍 Find Cyber Security Jobs")
job_query = st.text_input("Search for Cyber Security Jobs")
if st.button("Search Jobs"):
    job_results = recommend_jobs_based_on_resume(job_query)
    for job in job_results:
        st.write(f"### {job['Job Role']}")
        st.write(f"🏢 **Company:** {job['Company']}")
        st.write(f"📍 **Location:** {job['Location']}")
        st.write(f"💼 **Experience Required:** {job['Experience']}")
        st.write(f"💰 **Salary Range:** {job['Salary']}")
        st.write(f"🛠 **Skills Required:** {job['Skills']}")
        st.markdown(f'<a href="{job["Apply Link"]}" target="_blank"><button style="background-color: #007bff; color: white;">Apply Now</button></a>', unsafe_allow_html=True)

# ========== RESUME UPLOAD FEATURE ==========
st.subheader("📂 Upload Your Resume for AI-Based Job Recommendations")
uploaded_resume = st.file_uploader("Upload your Resume (PDF/DOCX)", type=["pdf", "docx"])
if uploaded_resume:
    resume_text = extract_text_from_resume(uploaded_resume)
    st.success("✅ Resume Uploaded Successfully!")
    if st.button("Get AI-Recommended Jobs"):
        recommended_jobs = recommend_jobs_based_on_resume(resume_text)
        st.subheader("🎯 Recommended Jobs Based on Your Resume")
        for job in recommended_jobs:
            st.write(f"### {job['Job Role']}")
            st.write(f"🏢 **Company:** {job['Company']}")
            st.write(f"📍 **Location:** {job['Location']}")
            st.write(f"💼 **Experience Required:** {job['Experience']}")
            st.write(f"💰 **Salary Range:** {job['Salary']}")
            st.write(f"🛠 **Skills Required:** {job['Skills']}")
            st.markdown(f'<a href="{job["Apply Link"]}" target="_blank"><button style="background-color: #007bff; color: white;">Apply Now</button></a>', unsafe_allow_html=True)
    
    # ========== RESUME OPTIMIZATION ==========
    job_desc = st.text_area("Paste a Job Description to Optimize Your Resume")
    if st.button("Optimize Resume"):
        optimized_resume = optimize_resume(resume_text, job_desc)
        st.subheader("✨ Optimized Resume")
        st.text_area("Here’s your optimized resume:", optimized_resume, height=300)

# Footer
st.markdown("---")
st.markdown("👨‍💻 Developed by **Dr. Chaitanya Tottadi**")
