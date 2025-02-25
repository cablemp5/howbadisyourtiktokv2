import json
import random
import re
import time
import zipfile
import pandas as pd
import streamlit as st
from concurrent.futures import as_completed
from io import StringIO, BytesIO
from google import genai
from requests_futures.sessions import FuturesSession

num_links_to_parse = 0
num_links_to_analyze = 0
num_items_to_show = 0

TAG_IGNORE = ["#fyp", "#viral", "#foryou", "fy", "#foryoupage", "#trending",
              "#fyp", "#fypシ゚viral", "#fypシ", "#blowthisup",
              "#fyppppppppppppppppppppppp", "#fy", "#fypage", "#viralvideo",
              "#xyzbca"]

st.set_page_config(
    page_title="how bad is your tiktok?",
    page_icon="🤢",
    initial_sidebar_state='collapsed',
    menu_items={"Get help":"https://github.com/cablemp5/how-bad-is-your-tiktok","Report a Bug":"https://github.com/cablemp5/how-bad-is-your-tiktok/issues","About":"This is the about section"}
)

with open( "style.css" ) as css:
  st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

def gemini_analysis(payload):

  client = genai.Client(api_key=st.secrets.key)
  prompt = st.secrets.prompt

  with (st.spinner('**judging your feed...**')):
    try:
      response = client.models.generate_content(model="gemini-2.0-flash",
                                                contents=[
                                                  prompt + str(payload)])
      return response.text
    except Exception as e:
      return e

def parse_tiktok_links(zip_file, selection):
  with zipfile.ZipFile(zip_file, 'r') as z:
    with z.open('user_data_tiktok.json') as f:
      html_data = json.load(f)

  links = []
  liked_videos = [i["link"] for i in
                  html_data["Activity"]["Like List"]["ItemFavoriteList"]]
  saved_videos = [i["Link"] for i in
                  html_data["Activity"]["Favorite Videos"]["FavoriteVideoList"]]

  if "Liked" in selection and "Saved" in selection:
    while liked_videos or saved_videos:
      if liked_videos:
        links.append(liked_videos.pop(0))
      if saved_videos:
        links.append(saved_videos.pop(0))
  elif "Liked" in selection:
    links = liked_videos
  elif "Saved" in selection:
    links = saved_videos

  return list(set(links))

def sort_dict(dictionary):
  sorted_dict = (
    dict(sorted(dictionary.items(), key=lambda x: x[1], reverse=True)))

  for to_pop in TAG_IGNORE:
    sorted_dict.pop(to_pop, None)

  return sorted_dict

def scrape_tiktok(links, st_progress_bar):

  description_list = []
  hashtag_dict = {}
  username_dict = {}
  avatar_dict = {}

  num_to_scrape = min(num_links_to_parse, len(links))
  num_scraped = 0
  start_time = time.time()

  with FuturesSession() as session:
    futures = [session.get(links[i]) for i in range(min(num_links_to_parse, len(links)))]

    for future in as_completed(futures):
      response = future.result()
      response.raw.chunked = True
      response.encoding = 'utf-8'
      html = response.text

      num_scraped += 1
      elapsed_time = time.time() - start_time
      avg_time_per_video = elapsed_time / num_scraped
      remaining_time = (num_to_scrape - num_scraped) * avg_time_per_video

      eta_minutes = int(remaining_time // 60)
      eta_seconds = int(remaining_time % 60)

      st_progress_bar.progress(num_scraped / num_to_scrape,
                               text=f":gray[{num_scraped}/{num_to_scrape}]   **|   ⏳ time remaining - {eta_minutes:02d}:{eta_seconds:02d}**")
      description = re.search('\"desc\":\"([^\"]+)\"', html)
      if not description:
        description = ""
      else:
        description = description.group(1)
      description_list.append(description)

      username = re.search('\"uniqueId\":\"([^\"]+)\",\"nickname\":\"([^\"]+)\"', html)
      if not username:
        username = "Name Unavailable"
      else:
        username = "@" + username.group(1)
      username_dict.setdefault(username, 0)
      username_dict[username] += 1

      avatar = re.search('\"avatarMedium\":\"([^\"]+)\"', html)
      if not avatar:
        avatar = ""
      else:
        avatar = avatar.group(1).replace("\\u002F", "/")
      avatar_dict[username] = avatar

      hashtags = re.findall("#\S+", description)
      for tag in hashtags:
        hashtag_dict.setdefault(tag, 0)
        hashtag_dict[tag] += 1

  session.close()
  time.sleep(0.5)
  st_progress_bar.empty()

  return description_list, hashtag_dict, username_dict, avatar_dict

def on_upload(zip_file, selection, st_progress_bar):
  links = parse_tiktok_links(zip_file, selection)

  description_list, hashtag_dict, username_dict, avatar_dict = scrape_tiktok(
      links, st_progress_bar)

  sorted_hashtags = sort_dict(hashtag_dict)
  sorted_users = sort_dict(username_dict)

  if "Name Unavailable" in sorted_users:
    del sorted_users["Name Unavailable"]

  num_hashtags_to_show = min(num_items_to_show, len(sorted_hashtags))
  top_hashtags_to_show = dict(list(sorted_hashtags.items())[:num_hashtags_to_show])

  num_users_to_show = min(num_items_to_show, len(sorted_users))
  top_users = dict(list(sorted_users.items())[:num_users_to_show])

  num_hashtags_to_analyze = min(num_links_to_analyze, len(sorted_hashtags))
  top_hashtags_to_analyze = dict(list(sorted_hashtags.items())[:num_hashtags_to_analyze])

  description_str = str(description_list)
  prompt = str(top_hashtags_to_analyze) + description_str

  gemini_result = gemini_analysis(prompt)

  return top_users, top_hashtags_to_show, avatar_dict, gemini_result

def stream_data(text):
  for word in text.split(" "):
    yield word + " "
    time.sleep(random.random() * 0.1)


def update_checkbox():
  st.session_state.show_text_input = not st.session_state.checkbox_state
  st.rerun()


# st.image("https://i.postimg.cc/BnLW2WLk/favicon.png", width=100)
st.title("how bad is your tiktok?")

st.subheader("📂 download your data:")
with st.expander("**📋 instructions**"):
  st.write(
      "**1.** Follow the official [TikTok data request guide](https://support.tiktok.com/en/account-and-privacy/personalized-ads-and-data/requesting-your-data) to download your data")
  st.write("**2.** When prompted, select the following settings using the reference images below:")
  st.image("https://i.postimg.cc/HL2D6k0R/darkinstructionsrounded.png",
           use_container_width=True)
  st.write(
      '**3.** Upload the :green[TikTok_Data_XXXXXXXXXX.zip] file below and click  **🚀 judge my feed**')

st.subheader("📤 upload your data:")

uploaded_file = st.file_uploader(
    "**Upload the .zip file containing your TikTok Data:**", type=".zip",
    accept_multiple_files=False,
    help="Check the Help section to learn how to download the correct data",
    label_visibility='collapsed'
)

with st.popover("**settings**", icon="⚙️",
                  use_container_width=True):
  to_parse = st.slider("**📺 videos to scan**:", min_value=10,
                       max_value=5000, value=1000,
                       help="Default: 1000 videos")
  to_analyze = st.slider("**📝 hashtags to scan:**", min_value=10,
                         max_value=500, value=500,
                         help="Default: all hashtags (up to 500)")
  to_show = st.slider("**👁️‍🗨️ items to preview:**",
                      min_value=3, max_value=100, value=20,
                      help="Default: 20 hashtags/users (up to 100)")

if st.button(label="**🚀 judge my feed**", use_container_width=True,
               type="secondary"):
  if uploaded_file is None:
    st.error("**💥 you haven't uploaded a file!**")
  else:
    zip_file = BytesIO(uploaded_file.getvalue())
    selection = ['Liked','Saved']

    num_links_to_parse = to_parse
    num_links_to_analyze = to_analyze
    num_items_to_show = to_show

    st.divider()

    st_progress_bar = st.progress(0)


    username_dict, hashtag_dict, pfp_dict, gemini_response = on_upload(
      zip_file,
      selection,
      st_progress_bar=st_progress_bar)


    hashtags_to_show = list(hashtag_dict.keys())[:num_items_to_show]
    hashtag_counts_to_show = [str(hashtag_dict[hashtag]) for hashtag in
                              hashtags_to_show]

    df1 = pd.DataFrame(
        list(zip(hashtags_to_show, hashtag_counts_to_show)),
        columns=["#", "number of videos"]
    )

    users_to_show = list(username_dict.keys())[:num_items_to_show]
    avatars_to_show = [pfp_dict.get(user, "") for user in users_to_show]
    numvideos_to_show = [str(username_dict[user]) for user in users_to_show]
    links_to_show = ["https://www.tiktok.com/" + user for user in
                     users_to_show]

    df2 = pd.DataFrame(
        list(zip(avatars_to_show, users_to_show, numvideos_to_show,
                 links_to_show)),
        columns=["avatar", "username", "# of videos", "link"]
    )




    st.header("**most frequent hashtags:**")

    col1a,col2a,col3a = st.columns([0.33,0.33,0.33])
    # col1a.subheader(f"🥇")
    # col2a.subheader(f"🥈")
    # col3a.subheader(f"🥉")
    col1a.subheader(f"🥇:gray[{hashtags_to_show[0]}]")
    col2a.subheader(f"🥈:gray[{hashtags_to_show[1]}]")
    col3a.subheader(f"🥉:gray[{hashtags_to_show[2]}]")
    col1a.write(f"**{hashtag_counts_to_show[0]} videos**")
    col2a.write(f"**{hashtag_counts_to_show[1]} videos**")
    col3a.write(f"**{hashtag_counts_to_show[2]} videos**")

    st.write("&nbsp;")

    st.dataframe(df1, hide_index=True, use_container_width=True)

    st.divider()

    st.header("**most frequent users:**")

    col1,col2,col3 = st.columns(3)
    col1.markdown('''
    <a href="''' + links_to_show[0] +'''">
    <img class="circle-image" src="''' + avatars_to_show[0] + ''''">
    </a>''',unsafe_allow_html=True,
    )
    col2.markdown('''
    <a href="''' + links_to_show[1] +'''">
    <img class="circle-image" src="''' + avatars_to_show[1] + ''''">
    </a>''',unsafe_allow_html=True,
                  )
    col3.markdown('''
    <a href="''' + links_to_show[2] +'''">
    <img class="circle-image" src="''' + avatars_to_show[2] + ''''">
    </a>''',unsafe_allow_html=True,
    )

    col1.subheader(f"🥇:gray[{users_to_show[0]}]")
    col2.subheader(f"🥈:gray[{users_to_show[1]}]")
    col3.subheader(f"🥉:gray[{users_to_show[2]}]")
    # col1.markdown('''
    # <h4>🥇'''+
    #               users_to_show[0] + '''
    # </h4>''',unsafe_allow_html=True,
    #               )
    # col2.markdown('''
    # <h4>🥈'''+
    #               users_to_show[1] + '''
    # </h4>''',unsafe_allow_html=True,
    #               )
    # col3.markdown('''
    # <h4>🥉'''+
    #               users_to_show[2] + '''
    # </h4>''',unsafe_allow_html=True,
    #               )
    col1.write(f"**{numvideos_to_show[0]} videos**")
    col2.write(f"**{numvideos_to_show[1]} videos**")
    col3.write(f"**{numvideos_to_show[2]} videos**")

    st.write(" ")


    st.dataframe(df2, hide_index=True,
                 column_config={"link": st.column_config.LinkColumn("Link"),
                                "avatar": st.column_config.ImageColumn()},
                 use_container_width=True)

    st.divider()

    if isinstance(gemini_response, Exception):
      st.error(
          f'**👾 there was an unexpected error generating your AI analysis. check the "help" section for more info:**\n\n:red[`{str(gemini_response)}`]')
    else:
      st.header("**🖨️ ai analysis:**")
      prefix = "\> "
      formatted_response = re.sub(r'(^|\n\n)(\S)', rf'\1{prefix}\2', gemini_response)
      st.write_stream(stream_data(formatted_response))