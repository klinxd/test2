# -*- codeing = utf-8 -*-
# @Time :  2021/8/22 20:25
# @File : main.py
# @Software : PyCharm
import re
import sqlite3
import urllib.request
from bs4 import BeautifulSoup
import xlwt
import sqlite3
import pymysql

findLink = re.compile(r'<a href="(.*?)">')    #创建正则表达式对象，电影链接
movieName = re.compile(r'<span class="title">(.*?)</span>')      #电影名称
scord = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>')  #电影评分
assessNum = re.compile(r'<span>(.*?)人评价</span>')   #评价人数
description = re.compile(r'<p class="">(.*?)</p>',re.S)   #电影描述

#请求网页并返回网页字符串
def askHtml(baseUrl):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
    }
    req = urllib.request.Request(baseUrl,headers=header)
    respone = urllib.request.urlopen(req).read()
    #print(respone.read().decode('utf-8'))
    return respone

#解析网页数据，并把所需要的字段存放在集合中
def getDataHtml(baseUrl):
    moviesDataList = []       #所有电影数据信息

    #遍历10个网页信息
    for i in range(1):
        html = askHtml(baseUrl+str(i*25))

        # 逐一解析网页
        bs = BeautifulSoup(html,"html.parser")      #通过bs中html.parser解析器解析刚才拿到的html字符串,生成一个css对象
        movies = bs.findAll(class_="item")
        #遍历当前网页25个电影
        for movie in movies:
            movieData = []  # 单个电影信息数据
            item = str(movie)
            #获取电影中文名称和外国名称
            movName = re.findall(movieName,item)
            if len(movName) ==1:
                movieData.append(movName[0])    #将电影名称放入单个电影集合
                movieData.append(" ")
            elif len(movName) > 1:
                movieData.append(movName[0])
                movieData.append(movName[1].strip().replace('/',''))
            #获取电影链接
            link = re.findall(findLink, item)[0]
            movieData.append(link)      #将电影链接放入单个电影集合
            #电影评分
            score = re.findall(scord,item)[0]
            movieData.append(score)     #将电影评分放入单个电影集合
            #评价人数
            num = re.findall(assessNum,item)[0]
            movieData.append(num)       #将评价人数放入单个电影集合
            #电影描述
            scrip = re.findall(description,item)[0]
            scrip = re.sub('<br/>(\s+)',"",scrip)
            movieData.append(scrip.strip())
            moviesDataList.append(movieData)    #将每个电影放入所有电影集合中
    print(len(moviesDataList))
    return moviesDataList

#将数据存放在Excel中
def saveToExcel(list,fileName):
    excelObject = xlwt.Workbook(encoding='utf-8')       #创建excel对象
    excelSheet = excelObject.add_sheet('豆瓣电影Top250')    #创建sheet对象
    i = 0
    for movie in list:
        for j in range(len(movie)):
            excelSheet.write(i,j,movie[j])      #遍历电影集合数据写入sheet
        i +=1
    excelObject.save(fileName)      #保存数据到excel文件中

#创建数据库表
def createTable(dbName,tableName):
    doubanDb = pymysql.connect(host='192.168.150.100', user='root', password='rootmysql', port=3306, db=dbName)  # 连接数据库
    cur = doubanDb.cursor()  # 获取数据库游标
    creatSql = f'''
            create table {tableName}
                (id int primary key auto_increment,
                movieName varchar(50),
                foreiName varchar(50),
                link varchar(50),
                score FLOAT,
                judeg int,
                script varchar(100)
                )       
        '''  # 创建表语句
    cur.execute(creatSql)  # 创建douban表
    cur.close()
    doubanDb.close()

#数据库插入数据
def saveToDB(list,dbName,tableName):
    doubanDb = pymysql.connect(host='192.168.150.100', user='root', password='rootmysql', port=3306, db=dbName)  # 连接数据库
    cur = doubanDb.cursor()  # 获取数据库游标
    #将电影数据存入数据库
    for movie in list:
        for j in range(len(movie)):
            if j == 3 or j ==4:
                continue
            movie[j] = '"' + movie[j] + '"'
        movstr = ','.join('%s'%id for id in movie)      #将集合中元素用逗号连接起来
        addSql = f'insert into {tableName}(movieName,foreiName,link,score,judeg,script) values(%s)'%movstr        #将集合中的元素用逗号连接，形成sql语句
        #print(addSql)
        cur.execute(addSql)       #执行sql写入数据库
        doubanDb.commit()
    cur.close()
    doubanDb.close()

#主程序方法
def main():

    #获取网页数据
    baseUrl = 'https://movie.douban.com/top250?start='
    moviesList = getDataHtml(baseUrl)

    # #保存数据到Excel
    # fileName = 'douban.xls'
    # saveToExcel(moviesList,fileName)

    #保存数据到数据库
    dbName = 'python'
    tableName = 'douban'
    createTable(dbName,tableName)
    saveToDB(moviesList,dbName,tableName)
    print('数据库写入成功')

#程序入口
if __name__ == '__main__':
    main()


