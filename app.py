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
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AI Code Explainer", layout="wide")
st.title("🧠 AI Code Explainer & Analyzer")
st.write("Upload legacy code files (Python, C, C++, COBOL, Fortran, etc.), and get structured, junior-friendly explanations with complexity rating, vulnerabilities, and SOLID principle analysis.")

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

uploaded_files = st.file_uploader("📂 Upload code files", type=[allowed_ext], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        code = uploaded_file.read().decode("utf-8")

        st.subheader(f"📄 Code Preview: {uploaded_file.name}")
        st.code(code, language=selected_lang.lower())

        if st.button(f"🧠 Analyze {uploaded_file.name}", key=uploaded_file.name):
            with st.spinner("Analyzing code with OpenAI..."):
                prompt = f"""
Analyze the following {selected_lang} code and explain it in simple terms for a junior developer. Rate the code complexity (1 to 10), explain vulnerabilities, and check if it follows SOLID principles. Format your response in JSON with keys: explanation, complexity_score, complexity_reason, vulnerabilities, solid_principles.

```{selected_lang.lower()}
{code}
```
"""
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5
                )

                try:
                    json_result = json.loads(response.choices[0].message.content)
                except:
                    st.error("❌ Couldn't parse the AI response. Please try again.")
                    st.stop()

                st.success("✅ Analysis Complete")

                st.subheader("📘 Explanation")
                st.write(json_result.get("explanation", "N/A"))

                st.subheader("📏 Code Complexity")
                complexity = json_result.get("complexity_score", 0)
                st.metric("Rating (1–10)", complexity)

                if complexity <= 3:
                    st.success("🟢 Easy to understand")
                elif complexity <= 6:
                    st.warning("🟡 Moderate complexity")
                else:
                    st.error("🔴 High complexity")

                st.markdown(f"**Why?** {json_result.get('complexity_reason', 'N/A')}")

                st.subheader("📊 Complexity Visualization")
                fig, ax = plt.subplots()
                sns.barplot(x=["Complexity"], y=[complexity], ax=ax)
                ax.set_ylim(0, 10)
                ax.set_ylabel("Score")
                ax.set_title("Code Complexity")
                st.pyplot(fig)

                st.subheader("🔐 Vulnerabilities")
                st.write(json_result.get("vulnerabilities", "No critical issues found."))

                st.subheader("🧩 SOLID Principle Check")
                st.write(json_result.get("solid_principles", "Not applicable."))

                st.subheader("🧪 Linting Suggestions")
                lint_prompt = f"Suggest linting improvements or formatting fixes for this code:\n```{selected_lang}\n{code}\n```"
                lint_response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": lint_prompt}]
                )
                st.code(lint_response.choices[0].message.content)

                st.subheader("📥 Download JSON Report")
                json_str = json.dumps(json_result, indent=2)
                st.download_button(
                    "📁 Download JSON",
                    data=json_str,
                    file_name=f"{uploaded_file.name}_report.json",
                    mime="application/json"
                )

                st.subheader("📑 Download PDF Report")
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, f"Code Analysis Report for {uploaded_file.name}\n\n")
                for k, v in json_result.items():
                    pdf.multi_cell(0, 10, f"{k.upper()}:\n{v}\n\n")
                pdf_output = f"/tmp/{uploaded_file.name}_report.pdf"
                pdf.output(pdf_output)

                with open(pdf_output, "rb") as f:
                    st.download_button(
                        label="📄 Download PDF",
                        data=f.read(),
                        file_name=f"{uploaded_file.name}_report.pdf",
                        mime="application/pdf"
                    )
