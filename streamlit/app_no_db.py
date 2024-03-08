# streamlit_app.py
import datetime
from llm_utils import text_format
from llm_utils.streamlit_common import apply_uab_font, hide_streamlit_branding
import Grant_Guide.generate as grant_generate
import Grant_Guide_config.app_config as grant_helper_app_config
import Grant_Guide_config.boilerplate as Grant_boilerplate
import Grant_Guide_config.config as Grant_Guide_config
import streamlit as st

def show_grant_guide_page(vectorstore=Grant_Guide_config.GRANT_VECTORSTORE):
    # Page metadata
    st.set_page_config(page_title="Grant Guide", page_icon="💰")
    # Hide streamlit branding
    hide_streamlit_branding()
    # Set font to UAB brand standard
    apply_uab_font()

    # Page content
    st.title("💰 Grant Guide 🤖")
    st.markdown("""
    **Get help writing NIH-style grants.**

    Brought to you by the Anesthesiology Research, Informatics, and Data Science teams.

    _Not approved for use with PHI._

    All submissions are recorded for potential review by departmental and health system personnel.

    ---
    """)

    tab1, tab2, tab3, tab4 = st.tabs(["Search and Compare", "Specific Aims", "Research Strategy", "F-Style Grants"])

    with tab1:
        st.write("Perform an AI-assisted search of the last 5 fiscal years' funded NIH grants and compare them to your idea. This search is limited to the following [NIH-RePORTER](https://reporter.nih.gov/advanced-search) departments: " + ", ".join(Grant_Guide_config.DEPARTMENTS))
        aims = st.text_area("Enter your specific aims:", height=300, key="aims_for_comparison")

        if st.button("Lookup and compare"):
            with st.spinner("Thinking..."):
                submit_time = datetime.datetime.now()
                documents = grant_generate.search_grant_guide_vectorstore(query=aims, store=vectorstore)
                result = grant_generate.get_grant_guide_response(query=aims, docs=documents)
                response_time = datetime.datetime.now()
                st.markdown(result.content)
                st.success("Your comparison has been generated.")

    with tab2:
        st.write("Get an AI-generated draft of your specific aims page and project summary/abstract.")
        aims = st.text_area("Enter your specific aims:", height=300, key="aims_for_page")

        if st.button("Draft specific aims page"):
            with st.spinner("Drafting. This may take a few minutes..."):
                submit_time = datetime.datetime.now()
                aims_result = grant_generate.get_aims_response(aims)
                response_time = datetime.datetime.now()
                summary_result = grant_generate.get_summary_response(aims_result.content)

                output_text = Grant_boilerplate.CONTRACT + "# AI-generated text \n\n## Specific Aims Page \n\n" + aims_result.content + "\n\n## Project Summary/Abstract \n\n" + summary_result.content
                aims_docx_data = text_format.convert_markdown_docx(output_text)

                if aims_docx_data:
                    st.balloons()
                    st.write("Note that once you hit download, this form will reset.")
                    st.download_button(label="Download aims draft", data=aims_docx_data, file_name="DRAFT_specific_aims_page.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    with tab3:
        st.write("Get an AI-generated draft of an element of your Research Strategy section.")
        research_strategy_part = st.selectbox("Which part of the Research Strategy do you need help with?", list(Grant_Guide_config.prefilled_text.keys()))

        strategy_bullets = st.text_area("Please address the following and replace the text in the box. **We suggest copying the instructions into a Word Doc and pasting your response when done.**", value=Grant_Guide_config.prefilled_text[research_strategy_part], height=650)

        if st.button("Draft specific strategy part"):
            with st.spinner("Preparing draft. This may take a few minutes..."):
                submit_time = datetime.datetime.now()
                strategy_result = grant_generate.get_strategy_response(bullet_points=strategy_bullets, rs_part=research_strategy_part, instructions=Grant_Guide_config.prefilled_text[research_strategy_part])
                response_time = datetime.datetime.now()

                output_text = Grant_boilerplate.CONTRACT + "# AI-generated text \n\n" + strategy_result.content
                strategy_docx_data = text_format.convert_markdown_docx(output_text)

                if strategy_docx_data:
                    st.balloons()
                    st.write("Note that once you hit download, this form will reset.")
                    st.download_button(label="Download strategy element draft", data=strategy_docx_data, file_name=f"DRAFT_{research_strategy_part}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    with tab4:
            st.write("Assistance with drafting F-Style (Fellowship) Grant applications.")
            f_grant_aims = st.text_area("Enter the key points of your Fellowship application:", height=300, key="f_grant_aims")

            if st.button("Generate F-Style Draft", key="f_style_draft"):
                with st.spinner("Generating draft for F-Style Grant..."):
                    submit_time = datetime.datetime.now()
                    # Assuming you have a function to generate F-Style grant content
                    f_grant_result = grant_generate.get_f_grant_response(f_grant_aims)
                    response_time = datetime.datetime.now()
                    st.markdown(f_grant_result.content)
                    st.success("Your F-Style Grant draft has been generated.")

                    # Optional: Implement any additional functionality such as downloading the draft as a document

if __name__ == "__main__":
    show_grant_guide_page()
