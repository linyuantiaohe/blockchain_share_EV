import streamlit as st
import json
import datetime
import blockchain as bc
import os

st.markdown('## 发布供给')

myid = st.text_input("请输入您的id", key='myid')

mylotid = st.text_input("请输入您的车位号", key='mylotid')

business_type = st.checkbox("是否需要交换车位？")

if business_type:
    business_type='SE'
else:
    business_type='SN'

new_bc=bc.Blockchain()

if os.path.exists('./chains/latest_blockchain.json'):
    with open('./chains/latest_blockchain.json',"r") as f:
        new_bc.chain=json.load(f)

today = datetime.datetime.now()
st.markdown('### 1. 请选择可以开始共享的时间')
startdate=st.date_input('请选择日期',value=today,min_value=today,max_value=datetime.datetime.now()+datetime.timedelta(days=7),key='startdate')

starttime=st.time_input('请选择时间', value="now",key='starttime')

st.write(starttime)

st.markdown('### 2. 请选择结束共享的时间')
enddate=st.date_input('请选择日期',value=today,min_value=today,max_value=datetime.datetime.now()+datetime.timedelta(days=7),key='enddate')

endtime=st.time_input('请选择时间', value="now",key='endtime')

st.markdown('### 3. 请输入价格')
price = st.number_input("请输入价格(元/次)",key='price')

agent_business_message=new_bc.add_agent_business_message(business_type,myid,mylotid,'%s %s'%(startdate,starttime),'%s %s'%(enddate,endtime),price)

if st.button("提交",key='submit'):
    new_bc.make_a_request(agent_business_message)
    if_fit,fit_list=new_bc.get_available_list(agent_business_message)
    if not os.path.exists('./chains/'):
        os.mkdir('./chains/')
    with open('./chains/latest_blockchain.json',"w") as f:
        json.dump(new_bc.chain,f)
    if if_fit:
        with open('./chains/bak_blockchain.txt',"w") as f:
            f.write('')

if os.path.exists('./chains/bak_blockchain.txt'):
    st.write("发布成功.检测到匹配需求,请选择是否达成合约?")
    if_fit,fit_list=new_bc.get_available_list(agent_business_message)
    available_dict={i:"%s--%s"%(i,new_bc.chain[i]['business_message']) for i in fit_list}
    available_dict[0]='0--放弃'
    option=(st.selectbox('选择待匹配需求:',available_dict.values())).split('--')[0]
    if st.button("确定",key='makedeal'):
        if option != '0':
            message_for_share,message_for_rent=new_bc.make_a_deal(business_type[1],len(new_bc.chain),int(option),mylotid,new_bc.chain[int(option)]['business_message'].split('|')[2],new_bc.chain[int(option)]['business_message'].split('|')[3],new_bc.chain[int(option)]['business_message'].split('|')[4],new_bc.chain[int(option)]['business_message'].split('|')[5])
            st.write(message_for_share)
            os.remove('./chains/bak_blockchain.txt')
            if not os.path.exists('./chains/'):
                os.mkdir('./chains/')
            with open('./chains/latest_blockchain.json',"w") as f:
                json.dump(new_bc.chain,f)
        else:
            st.write('继续等待.稍后如有匹配成功,会发出通知.')
else:
    st.write('发布成功.暂无匹配需求.稍后如有匹配成功,会发出通知.')