import streamlit as st

with open( "style.css" ) as css:
  st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.title("📢 disclaimer")
st.warning(
    "️️By using this website, you acknowledge that analyzing your TikTok activity requires uploading your TikTok data and, optionally, providing a Gemini API key. **All data remains private and is neither stored nor viewed by anyone other than you and Google's Gemini AI**. For your security, please avoid including any personally identifiable information in the data you upload. Additionally, if you choose to use a Gemini API key, we recommend generating a new key that is not linked to any other projects to ensure the integrity and security of your data.")