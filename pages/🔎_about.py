import streamlit as st

with open( "style.css" ) as css:
  st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.title("🔎 about")

st.info(
    "✨ This project was heavily inspired by [**How Bad Is Your Streaming Music?**](https://pudding.cool/2021/10/judge-my-music/) by The Pudding!")
st.write(
    'Curious what **A.I.** really thinks of your TikTok feed? This self-proclaimed "content-connoisseur" will judge your liked videos and provide a brutally honest—*and painfully accurate*—assessment of your digital footprint.')

