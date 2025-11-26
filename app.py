import streamlit as st
import pandas as pd
import numpy as np

st.title('아~내가드디어 다커서 앱도 만들고')

st.write("기특하기 짝이 없는 저의 개쩌는 앱을 보세요:")
st.write(pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
}))

st.markdown(
    """
    This is a playground for you to try Streamlit and have fun.
    
    **There's :rainbow[so much] you can build!**
    
    we prepared a few examples for you to get started. Just click on the buttons above and discover what you can do with Streamlit.
    """
)

if st.button("별풍선 쏘기"):
    st.balloons()

