import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from io import BytesIO
import openai

# Load environment
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Page setup
st.set_page_config(page_title="CodeClarity – AI Code Analyzer", layout="wide")
st.title("🧠 CodeClarity – AI Code Analyzer")
st.markdown("""
Welcome to **CodeClarity**, your intelligent assistant for understanding legacy and modern code.
Upload code files, and get detailed explanations, complexity analysis, vulnerability checks, SOLID principle insights, and even linting tips!
""")

# Language options
languages = {
    "Python": "py",
    "C": "c",
    "C++": "cpp",
    "COBOL": "cbl",
    "Fortran": "f90",
    "C#": "cs"
}

selected_lang = st.selectbox("📌 Select Programming Language", list(languages.keys()))
allowed_ext = languages[selected_lang]

uploaded_files = st.file_uploader(
    "📂 Upload code files (you can upload multiple)",
    type=[allowed_ext],
    accept_multiple_files=True
)
def generate_pdf_report(data, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"CodeClarity Report for {filename}\n\n")
    for k, v in data.items():
        if isinstance(v, list):
            v = "\n".join(v)
        elif isinstance(v, dict):
            v = json.dumps(v, indent=2)
        pdf.multi_cell(0, 10, f"{k.upper()}:\n{v}\n\n")

    # Return binary PDF content
    pdf_output = pdf.output(dest='S').encode('latin-1')  # return as bytes
    return BytesIO(pdf_output)

if uploaded_files:
    for uploaded_file in uploaded_files:
        code = uploaded_file.read().decode("utf-8")

        with st.expander(f"View Code – {uploaded_file.name}", expanded=False):
            st.code(code, language=selected_lang.lower())

        if st.button(f"Analyze {uploaded_file.name}", key=uploaded_file.name):
            with st.spinner("Analyzing the code..."):
                prompt = f"""
Analyze the following {selected_lang} code and explain it in simple terms for a junior developer. 
Return JSON with:
- explanation
- complexity_score (1 to 10)
- complexity_reason
- vulnerabilities
- solid_principles

```{selected_lang.lower()}
{code}
```
"""
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5
                )

                try:
                    json_result = json.loads(response.choices[0].message.content)
                except Exception:
                    st.error("Could not parse response. Please retry.")
                    st.stop()

                st.success("Code Analysis Completed")

                st.header("Explanation")
                st.write(json_result.get("explanation", "N/A"))

                st.subheader("Complexity Score")
                complexity = json_result.get("complexity_score", 0)
                st.metric("Score (1-10)", complexity)
                st.markdown(f"Reason: {json_result.get('complexity_reason', 'N/A')}")

                st.subheader("Complexity Visualization")
                fig, ax = plt.subplots()
                sns.barplot(x=["Complexity"], y=[complexity], palette="Blues_d", ax=ax)
                ax.set_ylim(0, 10)
                ax.set_ylabel("Score")
                ax.set_title("Code Complexity")
                st.pyplot(fig)

                st.subheader("Vulnerability Check")
                st.write(json_result.get("vulnerabilities", "No known vulnerabilities detected."))

                st.subheader("SOLID Principle Analysis")
                st.write(json_result.get("solid_principles", "Not applicable for this code."))

                st.subheader("Linting & Formatting Suggestions")
                lint_prompt = f"Suggest linting and formatting improvements for this {selected_lang} code:\n```{selected_lang.lower()}\n{code}\n```"
                lint_response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": lint_prompt}]
                )
                st.code(lint_response.choices[0].message.content)

                st.subheader("Download Reports")
                json_str = json.dumps(json_result, indent=2)

                st.download_button(
                    "Download JSON Report",
                    data=json_str,
                    file_name=f"{uploaded_file.name}_report.json",
                    mime="application/json"
                )

                pdf_data = generate_pdf_report(json_result, uploaded_file.name)
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_data,
                    file_name=f"{uploaded_file.name}_report.pdf",
                    mime="application/pdf"
                )
