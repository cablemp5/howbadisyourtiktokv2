import streamlit as st

with open( "style.css" ) as css:
  st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.title("🚨 help")

st.error(
    'The website will use the testing/demo key by default. If you receive a :green[429 RESOURCE_EXHAUSTED] error, please create and use your own key! To use your own key toggle the "Use the testing/demo Gemini API key" box and proceed with the below instructions')
st.subheader("**generating a gemini API key:**")
st.write(
    "1\. Sign in with your Google account and create and your Gemini API key [here](https://aistudio.google.com/app/apikey)")
st.write("2\. After signing in, select the option to use the Gemini API and accept the terms and conditions")
st.write("3\. Generate your API key and copy it, using the reference images below for guidance")
st.image("https://i.postimg.cc/d07NyQHG/inst1rounded.png",
         use_container_width=True)
st.image("https://i.postimg.cc/cCcFSvCG/inst2rounded.png",
         use_container_width=True)
st.write(
    '4\. Toggle :green[Use the testing/demo Gemini API key] to :red[OFF] and paste the copied API key into the text input field labeled **"Enter your Gemini API Key:"**')