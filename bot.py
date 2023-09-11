from flask import Flask, request
import requests
import json
import openai
import random
from lxml import etree
app = Flask(__name__)
qq_no = "1667513537"
API = "sk-"
headers={
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
}
class API:
    @staticmethod
    def send(message):
        url = "http://127.0.0.1:5678/send_msg"
        data = request.get_json()
        message_type = data['message_type']
        if 'group' == message_type:
            group_id = data['group_id']
            params = {
                "message_type": message_type,
                "group_id": str(group_id),
                "message": message
            }
        else:
            user_id = data['user_id']
            params = {
                "message_type": message_type,
                "user_id": user_id,
                "message": message
            }
        requests.get(url, params=params)

    @staticmethod
    def pic(tagc):
        tag = "&tag=" + tagc
        if tagc == "无":
            urls = "https://api.lolicon.app/setu/v2?r18=0"
        else:
            urls="https://api.lolicon.app/setu/v2?r18=0"+tag
        response = requests.get(urls)
        if response.status_code == 200:
            data = json.loads(response.content)
            original_url = data['data'][0]['urls']['original']
        API.send("[CQ:image,file="+str(original_url)+"]")

    @staticmethod
    def newpic(taginf):
        sort = "&sort=" + str(taginf)
        urls = "https://moe.jitsu.top/img/?&size=original&type=json" + str(sort)
        response = requests.get(urls)
        if response.status_code == 200:
            data = json.loads(response.content)
            img = data['pics'][0]
        API.send("[CQ:image,file=" + str(img) + "]")

    @staticmethod
    def chat(message):
        openai.api_key = API
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        response = completion.choices[0].message.content
        return(response)

    @staticmethod
    def drew(message):
        openai.api_key = API
        # 使用 OpenAI API 生成图片
        response = openai.Image.create(
            prompt=message,
            n=1,
            size="1024x1024"
        )
        # 获取生成的图片数据
        image_data = response['data'][0]['url']
        API.send("[CQ:image,file="+str(image_data)+"]")
    @staticmethod
    def wheteher(city):
        urls = "https://api.vvhan.com/api/weather?city="+str(city)
        response = requests.get(urls)
        if response.status_code == 200:
            data = json.loads(response.content)
            whe = data['city'] + data['info']['date'] + '天气为：\n' + data['info']['type'] + ',' + data['info'][
                'high'] + ',' + data['info']['low'] + ',' + data['info']['fengxiang'] + data['info'][
                      'fengli'] + '\ntip:' + data['info']['tip']
        API.send(whe)
class WCA:
    @staticmethod
    def getpage(u):
        x = 'https://cubingchina.com/results/person/' + u
        res = requests.get(url=x, headers=headers)
        tree = etree.HTML(res.text)
        name = []
        WCA = {}

        WCA['姓名'] = tree.xpath('//div[@class="panel panel-info person-detail"]/div/div/div[1]/span[2]/text()')[0]
        WCA['WCAID'] = tree.xpath('//div[@class="panel panel-info person-detail"]/div/div/div[4]/span[2]/text()')[0]
        WCA['地区'] = tree.xpath('//div[@class="panel panel-info person-detail"]/div/div/div[2]/span[2]/text()')[
            0].strip('\n').strip()
        WCA['参赛次数'] = tree.xpath('//div[@class="panel panel-info person-detail"]/div/div/div[3]/span[2]/text()')[0]
        WCA['性别'] = tree.xpath('//div[@class="panel panel-info person-detail"]/div/div/div[5]/span[2]/text()')[0]
        tbody = tree.xpath('/html/body/div[1]/div/div/div/div/div/div[3]/table/tbody')[0]
        rows = tbody.xpath('./tr')
        row_num = len(rows)
        for i in range(1, row_num):
            event = tree.xpath(f'//div[@class="table-responsive"]/table/tbody/tr[{i}]/td[1]/a//text()')[0]
            try:
                WCA[str(event) + '单次'] = \
                tree.xpath(f'//div[@class="table-responsive"]/table/tbody/tr[{i}]/td[5]/a//text()')[0]
            except Exception:
                WCA[str(event) + '单次'] = '无'
            try:
                WCA[str(event) + '平均'] = \
                tree.xpath(f'//div[@class="table-responsive"]/table/tbody/tr[{i}]/td[6]/a//text()')[0]
            except Exception:
                WCA[str(event) + '平均'] = '无'
        name.append(WCA)
        return name

    @staticmethod
    def get_wcaid(nam):
        url = 'https://cubing.com/results/person?region=World&gender=all&name=' + nam
        res = requests.get(url=url, headers=headers)
        tree = etree.HTML(res.text)
        ul = tree.xpath('//*[@id="yw1"]/table/tbody/tr/td[3]/text()')
        list = []
        for i in ul:
            list.append(i)
        return list

    @staticmethod
    def selct(search):
        id = WCA.get_wcaid(search)
        if len(id) == 1:
            wcaid = id[0]
            person = WCA.getpage(wcaid)
            output = ""
            for person in person:
                output += f"姓名: {person['姓名']}\tWCAID: {person['WCAID']}\t地区: {person['地区']}\t参赛次数: {person['参赛次数']}\t性别: {person['性别']}\n"
                for i, key in enumerate(person.keys()):
                    if i < 5:
                        continue  # 跳过已经输出的五个键
                    if i % 2 == 1:
                        output += f"{key}: {person[key]}\t"
                    else:
                        output += f"{key}: {person[key]}\n"
                output += "\n"  # 输出一个空行，使每个人的信息之间有一定间隔

            API.send(output)
        else:
            API.send(id)


@app.route('/', methods=["POST"])
def post_data():

    data = request.get_json()
    print(data)
    if data['post_type'] == 'message':
        message = request.get_json().get('raw_message')
        uid = request.get_json().get('sender').get('user_id')
        uidr = str(uid)
    if "来点涩图" in message:
        result = message.split()
        tagc = result[-1]
        API.pic(tagc)
    if str("[CQ:at,qq=%s]" % qq_no) in message:
        sender = request.get_json().get('sender')
        # 下面你可以执行更多逻辑，这里只演示与ChatGPT对话
        msg_text = API.chat(message)  # 将消息转发给ChatGPT处理
        msg_text = str('[CQ:at,qq=%s]\n' % uid) + str(msg_text)
        API.send(msg_text)
    if "绘图" in message:
        text_without_prefix = message.replace("绘图 ", "")
        API.drew(text_without_prefix)
    if ".来点图" in message:
        newtag= message.replace(".来点图 ", "")
        API.newpic(newtag)
    if "今日天气" in message:
        result = message.split()
        city = result[-1]
        API.wheteher(city)
    if ".wca" in message:
        result = message.split()
        search = result[-1]
        WCA.selct(search)


if __name__ == '__main__':
    # 此处的 host和 port对应上面 yml文件的设置
    app.run(host='0.0.0.0', port=5679)  # 保证和我们在配置里填的一致
