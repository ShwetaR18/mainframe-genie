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

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Page setup
st.set_page_config(page_title="CodeGenie – AI Code Analyzer", layout="wide")
st.title("🧠 CodeGenie – AI Code Analyzer")

st.markdown("""
Welcome to **CodeGenie**, your intelligent assistant for understanding legacy and modern code.
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

# Session state to store analysis results
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}

# PDF generation function
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

    pdf_output = pdf.output(dest='S').encode('latin-1')
    return BytesIO(pdf_output)

# Process uploaded files
if uploaded_files:
    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        code = uploaded_file.read().decode("utf-8")

        with st.expander(f"📄 View Code – {filename}", expanded=False):
            st.code(code, language=selected_lang.lower())

        if st.button(f"🔄 Reanalyze {filename}", key=f"reanalyze_{filename}"):
            if filename in st.session_state.analysis_results:
                del st.session_state.analysis_results[filename]
            st.experimental_rerun()

        if filename not in st.session_state.analysis_results:
            if st.button(f"Analyze {filename}", key=f"analyze_{filename}"):
                with st.spinner("Analyzing the code..."):
                    prompt = f"""
You are an AI code analyzer.

Analyze the following {selected_lang} code and return a strict JSON object with the following fields:

- "explanation": (string) a simplified explanation of what the code does
- "complexity_score": (integer, 1 to 10)
- "complexity_reason": (string) why that complexity score was assigned
- "vulnerabilities": (array of strings)
- "solid_principles": (dictionary with SOLID principle keys and observations)

Respond ONLY with a valid JSON. No markdown, no commentary.

```{selected_lang.lower()}
{code}
"""
                    response = openai.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.5
                    )

                    try:
                        json_result = json.loads(response.choices[0].message.content)
                        st.session_state.analysis_results[filename] = json_result
                    except Exception:
                        st.error("❌ Could not parse response. Please retry.")
                        st.stop()

        if filename in st.session_state.analysis_results:
            json_result = st.session_state.analysis_results[filename]
            st.success("✅ Code Analysis Completed")

            st.header("🧾 Explanation")
            st.write(json_result.get("explanation", "N/A"))

            st.subheader("📊 Complexity Score")
            complexity = json_result.get("complexity_score", 0)
            st.metric("Score (1–10)", complexity)
            st.markdown(f"**Reason:** {json_result.get('complexity_reason', 'N/A')}")

            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"""
                    <div style='text-align:center; font-size:60px; font-weight:bold; color:#ff9800;'>{complexity}</div>
                    <div style='text-align:center; font-size:24px; font-weight:500; color:#1976d2;'>
                        {"Very Simple" if complexity <= 2 else
                         "Simple" if complexity <= 4 else
                         "Moderate" if complexity <= 6 else
                         "Complex" if complexity <= 8 else
                         "Very Complex"}
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("<br><b>Scale:</b>", unsafe_allow_html=True)
                st.markdown("""
                - <span style='color:#98E4DB'>**1–2: Very Simple**</span><br>
                - <span style='color:#6AD04E'>**3–4: Simple**</span><br>
                - <span style='color:#FCD5AE'>**5–6: Moderate**</span><br>
                - <span style='color:#F6A5A5'>**7–8: Complex**</span><br>
                - <span style='color:#F77C7C'>**9–10: Very Complex**</span>
                """, unsafe_allow_html=True)

            with col2:
                labels = ["Very Simple", "Simple", "Moderate", "Complex", "Very Complex"]
                centers = [1.5, 3.5, 5.5, 7.5, 9.5]
                colors = ["#98E4DB", "#6AD04E", "#FCD5AE", "#F6A5A5", "#F77C7C"]

                if complexity <= 2:
                    highlight_idx = 0
                elif complexity <= 4:
                    highlight_idx = 1
                elif complexity <= 6:
                    highlight_idx = 2
                elif complexity <= 8:
                    highlight_idx = 3
                else:
                    highlight_idx = 4

                edge_colors = ['black' if i == highlight_idx else 'white' for i in range(len(colors))]
                linewidths = [2.5 if i == highlight_idx else 0.5 for i in range(len(colors))]

                fig, ax = plt.subplots(figsize=(6, 4))
                bars = ax.bar(
                    labels,
                    [2, 4, 6, 8, 10],
                    color=colors,
                    edgecolor=edge_colors,
                    linewidth=linewidths
                )

                ax.axhline(y=complexity, color='black', linestyle='--', label=f"Your Score: {complexity}")
                ax.set_ylabel("Score")
                ax.set_title("Code Complexity Rating")
                ax.legend()
                st.pyplot(fig)

            st.subheader("🔒 Vulnerability Check")
            st.write(json_result.get("vulnerabilities", "No known vulnerabilities detected."))

            st.subheader("🧱 SOLID Principle Analysis")
            st.write(json_result.get("solid_principles", "Not applicable."))

            st.subheader("🧹 Linting & Formatting Suggestions")
            lint_prompt = f"Suggest linting and formatting improvements for this {selected_lang} code:\n```{selected_lang.lower()}\n{code}\n```"
            lint_response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": lint_prompt}]
            )
            st.code(lint_response.choices[0].message.content)

            st.subheader("📥 Download Reports")
            json_str = json.dumps(json_result, indent=2)

            st.download_button(
                "⬇️ Download JSON Report",
                data=json_str,
                file_name=f"{filename}_report.json",
                mime="application/json"
            )

            pdf_data = generate_pdf_report(json_result, filename)
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_data,
                file_name=f"{filename}_report.pdf",
                mime="application/pdf"
            )
