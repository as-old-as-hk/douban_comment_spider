import pymysql
db=pymysql.connect(host='localhost',user='root',password='123456',port=3306)
cursor=db.cursor()
cursor.execute('SELECT VERSION()')
data=cursor.fetchone()
print('Database Version:',data)
cursor.execute("CREATE DATABASE douban DEFAULT CHARACTER SET utf8")
db.close()
db=pymysql.connect(host='localhost',user='root',password='123456',port=3306,db='douban')
cursor=db.cursor()
cursor.execute('SELECT VERSION()')
data=cursor.fetchone()
print('Database Version:',data)
sql="CREATE TABLE `movies`(`id` int(11) NOT NULL,`name` varchar(255) NOT NULL,`director` varchar(255) NOT NULL,`scriptwriter` varchar(255) NOT NULL,`actor` varchar(500) NOT NULL,`type` varchar(255) NOT NULL,`area` varchar(255) NOT NULL,`language` varchar(255) NOT NULL,`date` varchar(255) NOT NULL)DEFAULT CHARSET utf8;"
cursor.execute(sql)
sql="ALTER TABLE `movies` ADD PRIMARY KEY (`id`)"
cursor.execute(sql)
sql="CREATE TABLE `comments`(`id` int(11) NOT NULL,`user_name` varchar(255) NOT NULL,`movie_name` varchar(255) NOT NULL,`rate` int(11) NOT NULL)DEFAULT CHARSET utf8;"
cursor.execute(sql)
sql="ALTER TABLE `comments` ADD PRIMARY KEY (`id`)"
cursor.execute(sql)
db.close()