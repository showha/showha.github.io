import json
import tkinter as tk
import threading
import re
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import jieba
from tkinter import scrolledtext
from urllib import parse
import jsonpath as jsp
import os

cookies = {
    '__client_id': '',
    '_uid': ''
}

problem_list = []

difficulties = {
    1: "入门",
    2: "普及-",
    3: "普及/提高-",
    4: "普及+/提高",
    5: "提高+/省选-",
    6: "省选/NOI-",
    7: "NOI/NOI+/CTSC"
}

difficulties_reverse = {
    "入门": 1,
    "普及-": 2,
    "普及/提高-": 3,
    "普及+/提高": 4,
    "提高+/省选-": 5,
    "省选/NOI-": 6,
    "NOI/NOI+/CTSC": 7
}


class Problem:
    def __init__(self):
        self.url = ""
        self.pid = 1000
        self.difficulty = 0
        self.title = ""
        self.tags = []

    def setBase(self, baseUrl, pid):
        self.pid = pid
        self.url = baseUrl + str(pid)

    def setPrime(self, difficulty, title):
        self.difficulty = difficulty
        self.title = title

    def getBase(self):
        return self.url, self.pid

    def getPrime(self):
        return self.difficulty, self.title


def HTMLAuth(url):
    # 创建一个随机User-Agent生成器
    user_agent = UserAgent()

    # 设置请求头
    headers = {
        'User-Agent': user_agent.random,
    }
    session = requests.Session()
    for key in cookies:
        session.cookies[key] = cookies[key]

    response = session.get(url=url, headers=headers)

    # 检查是否登录成功
    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")

    # 关闭会话
    session.close()
    return response.text


def HTML(url):
    # 创建一个随机User-Agent生成器
    user_agent = UserAgent()

    # 设置请求头
    headers = {
        'User-Agent': user_agent.random,
    }
    response = requests.get(url, headers=headers)
    # 继续处理响应内容
    return response.text


def filterList():
    global problem_list
    if len(problem_list) != 0:
        return problem_list
    url = "https://www.luogu.com.cn/problem/list"
    base_url = "https://www.luogu.com.cn/problem/P"
    html = HTML(url=url)
    url_parse = re.findall('decodeURIComponent\((.*?)\)\)', html)[0]
    html_parse = json.loads(parse.unquote(url_parse)[1:-1])
    result_list = list(jsp.jsonpath(html_parse, '$.currentData.problems.result')[0])

    user_agent = UserAgent()
    headers = {'User-Agent': user_agent.random}
    tag_url = 'https://www.luogu.com.cn/_lfe/tags'
    tag_html = requests.get(url=tag_url, headers=headers).json()
    tags_dicts = [{'id': tag['id'], 'name': tag['name']} for tag in tag_html['tags'] if tag['type'] not in [1, 3, 4]]
    for information in result_list:
        problem = Problem()
        problem.pid = int(jsp.jsonpath(information, '$.pid')[0][1:])
        problem.title = jsp.jsonpath(information, '$.title')[0]
        problem.difficulty = int(jsp.jsonpath(information, '$.difficulty')[0])
        tags_s = list(jsp.jsonpath(information, '$.tags')[0])
        problem.tags = [tag_dict['name'] for tag_dict in tags_dicts if tag_dict['id'] in tags_s]
        problem_list.append(problem)

    return problem_list


def getProblemList(text, title='', algorithm="", difficulty=0, tag=''):
    text.delete('1.0', tk.END)
    problem_list = filterList()
    for problem in problem_list:
        if difficulty != 0 and difficulty != problem.difficulty:
            continue
        if algorithm != '' and algorithm not in problem.tags:
            continue
        if title != '':
            tid = re.search(r'P([1-9]\d{3})', title)
            if tid:
                title = tid.group(1)
            pid = str(problem.pid)
            title_text = jieba.lcut(problem.title)
            title_text.append(pid)
            title_text.append("P" + str(problem.pid))
            if title not in title_text:
                continue
        text.insert(tk.END, "P" + str(problem.pid) + "   " + problem.title + "\n")

    text.insert(tk.END, "题目查找完毕！\n")


# 界面切换函数

def crawl_problem(problem, base_url, output_text):
    try:
        url = base_url + str(problem.pid)
        html = HTML(url=url)
        bs = BeautifulSoup(html, "lxml")
        core = bs.select("article")[0]
        md = str(core)
        md = re.sub("<h1>", "# ", md)
        md = re.sub("<h2>", "## ", md)
        md = re.sub("<h3>", "#### ", md)
        md = re.sub("</?[a-zA-Z]+[^<>]*>", "", md)
        cfilename = './'
        cfilename += difficulties[problem.difficulty].replace("/", "_") + "-" + "-".join(problem.tags)
        if not os.path.exists(cfilename):
            os.mkdir(cfilename)
        cfilename += "/P" + str(problem.pid) + "-" + problem.title + ".md"
        with open(cfilename, "w", encoding="utf-8") as file:
            file.write(md)
        output_text.insert(tk.END, "P" + str(problem.pid) + "-" + problem.title + "...... 爬取成功" + "\n")
    except Exception as err:
        output_text.insert(tk.END, str(err) + "\n")


def crawl_problemSolu(problem, base_url, output_text):
    try:
        url = base_url + str(problem.pid)
        html = HTMLAuth(url=url)
        bs = BeautifulSoup(html, "lxml")
        js_code = bs.find("script").get_text()
        result = re.search(r'\(\"(.*)\"\)\)', js_code).group(1)
        python_code = parse.unquote(result)
        json_file = json.loads(python_code)
        solution = json_file["currentData"]["solutions"]["result"]
        md = solution[0]["content"]
        cfilename = './'
        cfilename += difficulties[problem.difficulty].replace("/", "_") + "-" + "-".join(problem.tags)
        if not os.path.exists(cfilename):
            os.mkdir(cfilename)
        cfilename += "/P" + str(problem.pid) + "-" + problem.title + "-题解" + ".md"
        with open(cfilename, "w", encoding="utf-8") as file:
            file.write(md)
        # output_text.insert(tk.END, "P" + problem + "......题解 爬取成功" + "\n")
        output_text.insert(tk.END, "P" + str(problem.pid) + "-" + problem.title + "......题解 爬取成功" + "\n")
    except Exception as err:
        output_text.insert(tk.END, str(err) + "\n")


# 题解爬取界面数据检查函数
def crawl_data(start_entry, end_entry, output_text):
    start = start_entry.get()
    end = end_entry.get()

    result1 = re.search(r'P([1-9][0-9]{3})', start)
    result2 = re.search(r'P([1-9][0-9]{3})', end)

    base_url = "https://www.luogu.com.cn/problem/P"

    if result1 and result2:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "正在爬取，请稍后\n")
        startI = int(result1.group(1)) - 1000
        endI = int(result2.group(1)) - 1000
        probleList = filterList()
        for problem in probleList[startI:endI+1]:
            crawl_problem(problem, base_url, output_text)
    else:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "数据不合法，请检查你的输入数据\n")

    output_text.insert(tk.END, "爬取完毕！\n")


def crawl_dataSolu(start_entry, end_entry, output_text):
    start = start_entry.get()
    end = end_entry.get()

    result1 = re.search(r'P([1-9][0-9]{3})', start)
    result2 = re.search(r'P([1-9][0-9]{3})', end)

    base_url = "https://www.luogu.com.cn/problem/solution/P"

    if result1 and result2:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "正在爬取，请稍后\n")
        startI = int(result1.group(1)) - 1000
        endI = int(result2.group(1)) - 1000
        probleList = filterList()
        # for i in range(startI, endI + 1):
        #     probleList.append(str(i))
        for problem in probleList[startI:endI+1]:
            crawl_problemSolu(problem, base_url, output_text)
    else:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "数据不合法，请检查你的输入数据\n")

    output_text.insert(tk.END, "爬取完毕！\n")


class MyGui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(1, 1)
        # self.root.minsize(500, 500)
        # self.root.geometry("600x300")
        self.root.title("洛谷爬题工具")
        self.page1 = tk.Frame(self.root)
        self.page2 = tk.Frame(self.root)
        self.main_page = tk.Frame(self.root)
        self.pages = [self.main_page, self.page1, self.page2]

    # 搜题界面
    def searchGui(self):
        page1 = self.page1
        difficulty_label = tk.Label(page1, text="题目难度")
        difficulty_label.pack()
        difficulty_var = tk.StringVar(value="")
        difficulty_choices = ["", "入门", "普及-", "普及/提高-", "普及+/提高", "提高+/省选-", "省选/NOI-",
                              "NOI/NOI+/CTSC"]
        difficulty_dropdown = tk.OptionMenu(page1, difficulty_var, *difficulty_choices)
        difficulty_dropdown.pack()
        # 创建两个输入框
        algorithm_label = tk.Label(page1, text="算法/来源")
        algorithm_label.pack()
        algorithm_entry = tk.Entry(page1)
        algorithm_entry.pack()
        title_label = tk.Label(page1, text="标题/题目编号")
        title_label.pack()
        title_entry = tk.Entry(page1)
        title_entry.pack()
        # 创建一个输出框
        text = scrolledtext.ScrolledText(page1, height=15, width=40, wrap=tk.WORD)
        # 创建提交按钮
        submit_button = tk.Button(page1, text="提交",
                                  command=lambda: self.multithread1(getProblemList, text, title_entry, algorithm_entry, difficulty_var))
        submit_button.pack()
        text.pack(pady=10)
        # 创建返回主页按钮
        button1 = tk.Button(page1, text="返回主界面", command=lambda: self.show_page(self.main_page))
        button1.pack()

    # 初始界面
    def mainGui(self):
        main_page = self.main_page
        label_main = tk.Label(main_page, text="洛谷爬题主页")
        label_main.pack(anchor='w', expand=tk.YES)
        button_page1 = tk.Button(main_page, text="搜题", command=lambda: self.show_page(self.page1))
        button_page1.pack(padx=10, pady=10)
        button_page2 = tk.Button(main_page, text="爬题", command=lambda: self.show_page(self.page2))
        button_page2.pack(padx=10, pady=10)

    # 爬题界面
    def downloadGui(self):
        page2 = self.page2
        label1 = tk.Label(page2, text="爬取题目与题解")
        label1.pack()
        start_label = tk.Label(page2, text="爬取的起始题目")
        start_label.pack()
        start_entry = tk.Entry(page2)
        start_entry.pack()
        end_label = tk.Label(page2, text="爬取的终止题目")
        end_label.pack()
        end_entry = tk.Entry(page2)
        end_entry.pack()
        crawl_button1 = tk.Button(page2, text="爬取题目",
                                  command=lambda: self.multithread2(start_entry, end_entry, output_text))
        crawl_button1.pack()
        crawl_button2 = tk.Button(page2, text="爬取题解",
                                  command=lambda: self.multithread3(start_entry, end_entry, output_text))
        crawl_button2.pack()
        output_text = tk.Text(page2, height=15, width=30)
        output_text.pack()
        back_button = tk.Button(page2, text="返回主界面", command=lambda: self.show_page(self.main_page))
        back_button.pack()
        # stop_button = tk.Button(page2, text="中止爬取", command=executor.shutdown) # 添加一个中止按钮
        # stop_button.pack()

    # 多线程启动方法一
    def multithread1(self, function, text, title_entry, algorithm_entry, difficulty_var):
        # 创建一个新线程
        t = threading.Thread(target=lambda: self.submit(function, text, title_entry, algorithm_entry, difficulty_var))
        # 启动线程
        t.start()

    def multithread2(self, start_entry, end_entry, output_text):
        t = threading.Thread(target=lambda: crawl_data(start_entry, end_entry, output_text))
        t.start()

    def multithread3(self, start_entry, end_entry, output_text):
        t = threading.Thread(target=lambda: crawl_dataSolu(start_entry, end_entry, output_text))
        t.start()

    # 定义提交函数
    def submit(self, function, text, title_entry, algorithm_entry, difficulty_var):
        # 获取参数
        title = title_entry.get()
        algorithm = algorithm_entry.get()
        if difficulty_var.get() != "":
            difficulty = difficulties_reverse[difficulty_var.get()]
        else:
            difficulty = 0

        # 调用后端函数
        # crawl(difficulty, algorithm, title)
        # getProblemList(title)
        function(text, title, algorithm, difficulty)

    # 切换界面
    def show_page(self, page):
        for p in self.pages:
            p.pack_forget()
        page.pack()

    # 显示初始界面
    def run(self):
        self.mainGui()
        self.searchGui()
        self.downloadGui()
        self.show_page(self.main_page)
        self.root.mainloop()


if __name__ == '__main__':
    myGui = MyGui()
    myGui.run()
