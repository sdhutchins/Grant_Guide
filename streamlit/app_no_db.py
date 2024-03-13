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
        aims = st.text_area("Enter your specific aims:", height=300, key="aims_for_page") # TODO: Insert placeholder aims

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
        st.write("Get an AI-generated draft for parts of your F-Style (Fellowship) Grant application.")

        f_grant_part = st.selectbox(
            "Which part of the F-Style Grant do you need help with?",
            ["Select a section"] + list(Grant_Guide_config.prefilled_text.keys()),  # Assuming you have similar prefilled text for F-Style Grants
            key="f_grant_part"
        )

        if f_grant_part != "Select a section":
            f_strategy_bullets = st.text_area(
                "Please address the following and replace the text in the box. **We suggest copying the instructions into a Word Doc and pasting your response when done.**",
                value=Grant_Guide_config.prefilled_text[f_grant_part],
                height=650,
                key="f_strategy_bullets"
            )

            if st.button("Draft F-Style Grant part", key="f_draft_part"):
                with st.spinner("Preparing draft for F-Style Grant part..."):
                    submit_time = datetime.datetime.now()
                    f_strategy_result = grant_generate.get_strategy_response(
                        bullet_points=f_strategy_bullets,
                        rs_part=f_grant_part,
                        instructions=Grant_Guide_config.prefilled_text[f_grant_part]
                    )
                    response_time = datetime.datetime.now()

                    output_text = Grant_boilerplate.CONTRACT + "# AI-generated text \n\n" + f_strategy_result.content
                    f_strategy_docx_data = text_format.convert_markdown_docx(output_text)

                    if f_strategy_docx_data:
                        st.balloons()
                        st.write("Note that once you hit download, this form will reset.")
                        st.download_button(
                            label="Download F-Style Grant part draft",
                            data=f_strategy_docx_data,
                            file_name=f"DRAFT_{f_grant_part}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )


if __name__ == "__main__":
    show_grant_guide_page()
