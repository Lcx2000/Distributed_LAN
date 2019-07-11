import pymysql

#连接数据库
#服务器，端口，用户名，密码，数据库名
conn = pymysql.connect(host='localhost',port=3306,user='root',password="lcx131547",database='test')

#获取游标
cursor = conn.cursor() 
cursor.execute('SELECT VERSION()')
data = cursor.fetchone()
print('Database version:', data)
# 建数据库
# cursor.execute("CREATE DATABASE test DEFAULT CHARACTER SET utf8")

#建表
# sql = """
# CREATE TABLE USER1 (
# id INT auto_increment PRIMARY KEY ,
# name CHAR(10) NOT NULL UNIQUE,
# age TINYINT NOT NULL
# )ENGINE=innodb DEFAULT CHARSET=utf8;  
# """
# cursor.execute(sql)

#插入
# sql = 'insert into USER1(name,age) values(%s,%s);'
# data = [
#     ('july', '47'),
#     ('june', '58'),
#     ('marin', '69')
# ]

# 拼接并执行sql语句
#cursor.executemany(sql, data)

# #删除
# sql = "DELETE FROM USER1 WHERE AGE > %s" % (60)

# 修改更新
sql = "UPDATE USER1 SET AGE = AGE + 1 WHERE name = '%s'" % ('june')

# 执行SQL语句
cursor.execute(sql)
# 涉及写操作需提交修改
conn.commit()

# SQL 查询语句
sql = "SELECT * FROM USER1 WHERE age > %s" % (50)
cursor.execute(sql)
# 获取所有记录列表
results = cursor.fetchall()
for row in results:
    id = row[0]
    name = row[1]
    age = row[2]
    print ("id=%s,name=%s,age=%s" % (id, name, age))

conn.close()
