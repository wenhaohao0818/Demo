# -*- coding: utf-8 -*-
# @Time : 2022/10/07 10:41
# @Author : wenhaohao

import requests
import json
import time
import csv
#以下需要修改
appcode="填自己的appcode"
phone = '填自己的手机尾号'
#以下不需要修改
headers = {
    'Authorization':'APPCODE ' + appcode
}

ex_status_flag={
    '-1':"待查询",
    '0':"查询异常",
    '1':"暂无记录",
    '2':"在途中",
    '3':"派送中",
    '4':"已签收",
    '5':"用户拒签",
    '6':"疑难件",
    '7':"无效单",
    '8':"超时单",
    '9':"签收失败",
    '10':"退回"
}

'''
    根据单号获取快递公司数据
'''
def getComByNu(num):
    req_data = {
    'nu': num,
    }
    #修改结束
    req_url="http://ali-deliver.showapi.com/fetchCom"
    try:
        html = requests.get(req_url, headers=headers,data=req_data)
    except :
        print("请求失败")
    return html.text

'''
    根据单号查询物流信息
'''
def getNuInfo(com,num):
    req_data = {
        'com': com,
        'nu': num,
        'receiverPhone': phone,#收件人手机尾号--查顺丰时候用
        'senderPhone': ''
    }
    req_url="http://ali-deliver.showapi.com/showapi_expInfo"
    try:
        html = requests.get(req_url, headers=headers,data=req_data)
    except :
        print("请求失败")
    return html.text

def readListTxt():
    exp_list = []
    tag_list = []
    with open("list.txt","r",encoding='utf-8') as f:
        tmp_list = f.read().splitlines()
        for item in tmp_list:
            print(item.split(' '))
            exp_list.append(item.split(' ')[0])
            if len(item.split(' '))==2:
                tag_list.append(item.split(' ')[1])
            else:
                tag_list.append("")
    return exp_list,tag_list

def main():
    # 读取单号列表和备注信息
    exp_list,tag_list = readListTxt()

    print(exp_list)
    print(tag_list)

    if len(exp_list)==0:
        print("没有单号可供查询!")
    else:
        # 创建CSV文件
        csvfile = open('{}-快递查询数据.csv'.format(time.strftime("%Y%m%d-%H%M%S")), 'w',newline='')  #打开方式还可以使用file对象
        writer = csv.writer(csvfile)
        writer.writerow(['序号', '单号', '快递公司','备注信息','运单信息','快递状态','更新时间','查询时间'])


        print("待查询单号:")
        print(exp_list)
        print("开始查询...")
        for inx,inv in enumerate(exp_list):
            print("正在查询{}/{}...".format(inx+1,len(exp_list)))

            com_data = json.loads(getComByNu(inv))
            ex_info = json.loads(getNuInfo(com_data['showapi_res_body']['data'][0]['comCode'],inv))

            print("查询次数:"+str(ex_info['showapi_res_body']['queryTimes']))
            print("快递单号:"+str(ex_info['showapi_res_body']['mailNo']))
            print("快递公司:"+ex_info['showapi_res_body']['expTextName'])
            print("状态:"+ex_info['showapi_res_body']['msg'])
            ex_info_data=ex_info['showapi_res_body']['data']
            print(ex_info_data)
            if ex_info['showapi_res_body']['ret_code']!=0:
                ex_info_data = [{"context":ex_info['showapi_res_body']['msg'],"time":""}]

            # 拼装成要写入的数据，与head一一对应
            tmp_data = [inx+1
                        ,str(ex_info['showapi_res_body']['mailNo'])+'\t'
                        ,ex_info['showapi_res_body']['expTextName']
                        ,tag_list[inx]
                        ,ex_info_data[0]['context']
                        ,ex_status_flag[str(ex_info['showapi_res_body']['status'])]
                        ,ex_info_data[0]['time']
                        ,ex_info['showapi_res_body']['updateStr']
            ]
            # 写入数据
            writer.writerow(tmp_data)
        print("已保存")
        csvfile.close()


if __name__=="__main__":
    main()