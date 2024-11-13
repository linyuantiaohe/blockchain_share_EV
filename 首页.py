import streamlit as st
import json
import blockchain as bc
import os

st.markdown('# 区块链电动汽车私桩共享模拟')

exist_bc=bc.Blockchain()

st.markdown('## 检查本地区块链')

uploaded_chain_file = st.file_uploader(
    "请上传本地区块链json文件", accept_multiple_files=False,key='uploaded_chain_file', type=['json']
    )

if uploaded_chain_file is not None:
    local_chain=json.load(uploaded_chain_file)
    if exist_bc.chain_valid(local_chain):
        exist_length=len(local_chain)

    if os.path.exists('./chains/latest_blockchain.json'):
        with open('./chains/latest_blockchain.json',"r") as f:
            latest_blockchain=json.load(f)
            if exist_bc.chain_valid(latest_blockchain):
                cloud_length=len(latest_blockchain)

    if cloud_length>exist_length:
        st.markdown('目前最新云端区块链编号为%s, 本地区块链低于该版本时应更新.'%(latest_blockchain[-1]['index']))

    elif cloud_length<exist_length:
        with open('./chains/latest_blockchain.json',"w") as f:
            json.dump(local_chain,f)

if os.path.exists('./chains/latest_blockchain.json'):
    with open('./chains/latest_blockchain.json','r') as file:
        btn = st.download_button(
            label="下载云端区块链",
            data=file,
            file_name="latest_blockchain.json",
            mime="text/json",
            key='download_chain'
            )