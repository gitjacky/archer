# archer
基于inception的自动化SQL操作平台，后期又针对公司具体需求对最初的archer平台做了二次开发，除基本SQL审核功能外，增加create index语法创建索引支持，添加公共字段latest_time自动审核提示，方便版本发布时多脚本管理(一个发布版本有多个sql文件)，同时增加工单搜索、工单语句修改、mongo接口同步与查询、版本工单一键上线其他环境、支持接入AD域(AD账户可直接登录本系统，系统会通过域进行认证，认证通过则会在本系统中创建用户账号，默认用户组为工程师。)等功能。

### 开发语言和推荐环境：
python：3.4<br/>
django：1.8.18<br/>
mysql : 5.6及以上<br/>
linux : 64位linux操作系统均可

### 主要功能：
* 自动审核：<br/>
  发起SQL上线，工单提交，由inception自动审核，审核通过后需要由审核人进行人工审核，支持create/drop index语法审核与执行。
* 人工审核：<br/>
  工单DBA人工审核、审核通过自动执行SQL.<br/>
  为什么要有人工审核？<br/>
  这是遵循运维领域线上操作的流程意识，一个工程师要进行线上数据库SQL更新，最好由另外一个工程师来把关.<br/>
  很多时候DBA并不知道SQL的业务含义，所以人工审核最好由其他研发工程师或研发经理来审核. 这是archer的设计理念.
* 回滚数据展示
* 主库集群配置
* 用户权限配置<br/>
  工程师角色（engineer）与审核角色（review_man）:工程师可以发起SQL上线，在通过了inception自动审核之后，需要由人工审核点击确认才能执行SQL.<br/>
  还有一个特殊的超级管理员即可以上线、审核，又可以登录admin界面进行管理.
* 历史工单管理，查看、修改、删除
* 可通过django admin进行匹配SQL关键字的工单搜索
* 发起SQL上线，可配置邮件提醒多个审核人进行审核
* 在发起SQL上线前，自助SQL审核，给出建议
* 版本工单提交，在一次发布中需执行多个SQL脚本文件，脚本文件存放在svn对应项目目录下的版本文件目录中，开发人员直接按项目路径选择版本目录，提交要发布的脚本。
* 版本工单一键上线其他环境，提交过某一个环境的版本SQL工单，可以直接一键上线其他环境，免去重复选择与提交。
* 版本工单页面有搜索栏用于搜索某段时间内某个环境提交与执行的所有版本工单，便于查找。
* Mongo接口同步，用于不同环境之间同步某个接口或MQ或定时器到另一个环境(接口分同步(2或4条记录)与异步接口(5条记录)，MQ(1条记录),定时器(1条记录))。
* Mongo接口、MQ、定时器查询，mongo编码查询页面可以使用编码名称查询对应mongo中的源记录内容。
* Mongo同步页面有批量编码搜索与提交，即搜索某段时间某个环境提交过的编码，可全选批量提交到别的环境。
* AD接入，使用ldap库，用户可直接登录本系统，若系统中已经有账号则由本系统负责验证并登录。若用户在本系统没有账号，且是第一次使用域账号登录，则系统会交由AD做验证，验证通过后在本系统上创建对应账号，用户默认组为工程师。
* DDL统计，主要是用于统计一段时间内开发环境一共审核并执行了多少条DDL语句，以库名称分组统计DDL数量并自动绘制条型图展示。
* 实例结构对比，主要用于不同实例间表结构不一致时的对比，生成对应的DDL语句与回滚语句。
* 开发SQL审核页面、MONGO与版本工单页面都有搜索栏，用于输入工单关键字/编码名称进行搜索。
* SQL审核必读中可加入SQL相关文档，用户可直接在本系统中阅读pdf文档。


### 设计规范：
* 合理的数据库设计和规范很有必要，尤其是MySQL数据库，内核没有oracle、db2、SQL Server等数据库这么强大，需要合理设计，扬长避短。互联网业界有成熟的MySQL设计规范，特此撰写如下。请读者在公司上线使用archer系统之前由专业DBA给所有后端开发人员培训一下此规范，做到知其然且知其所以然。<br/>
规范链接：  https://github.com/gitjacky/archer/blob/master/archer-master/docs/mysql_db_design_guide.md

### 主要配置文件：
* archer/archer/settings.py<br/>

### 安装步骤：
1. 环境准备：<br/>
(1)克隆代码到本地: git clone https://github.com/gitjacky/archer.git  或  下载zip包<br/>
(2)安装mysql 5.6实例，请注意保证mysql数据库默认字符集为utf8或utf8mb4<br/>
(3)安装inception<br/>
2. 安装python3：(强烈建议使用virtualenv或venv等单独隔离环境！)<br/>
tar -xzvf Python-3.4.1.tar.gz <br/>
cd Python-3.4.1 <br/>
./configure --prefix=/path/to/python3 && make && make install
或者rpm、yum、binary等其他安装方式
3. 安装所需相关模块：<br/>
(1)django：<br/>
tar -xzvf Django-1.8.17 && cd Django-1.8.17 && python3 setup.py install<br/>
或者pip3 install Django==1.8.17
(2)Crypto:<br/>
pip3 install Crypto<br/>
pip3 install pycrypto
4. 给python3安装MySQLdb模块:<br/>
pip3 install pymysql<br/>
记得确保settings.py里有如下两行：<br/>
import pymysql<br/>
pymysql.install_as_MySQLdb()<br/>
由于python3使用的pymysql模块里并未兼容inception返回的server信息，因此需要编辑/path/to/python3/lib/python3.4/site-packages/pymysql/connections.py：<br/>
在if int(self.server_version.split('.', 1)[0]) >= 5: 这一行之前加上以下这一句并保存，记得别用tab键用4个空格缩进：<br/>
self.server_version = '5.6.24-72.2-log'<br/>
最后看起来像这样：<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/pymysql.png)<br/>
5. 创建archer本身的数据库表：<br/>
(1)修改archer/archer/settings.py所有的地址信息,包括DATABASES和INCEPTION_XXX部分<br/>
(2)通过model创建archer本身的数据库表, 记得先去archer数据库里CREATE DATABASE<br/>
python3 manage.py makemigrations或python3 manage.py makemigrations sql<br/>
python3 manage.py migrate<br/>
执行完记得去archer数据库里看表是否被创建了出来<br/>
6. mysql授权:<br/>
记得登录到archer/archer/settings.py里配置的各个mysql里给用户授权<br/>
(1)archer数据库授权<br/>
(2)远程备份库授权<br/>
7. 创建admin系统root用户（该用户可以登录django admin来管理model）：<br/>
cd archer && python3 manage.py createsuperuser<br/>
8. 启动：<br/>
用django内置runserver启动服务,需要修改debug.sh里的ip和port<br/>
cd archer && bash debug.sh<br/>
如果要用gunicorn启动服务的话，可以使用pip3 install gunicorn安装并用startup.sh启动，但需要配合nginx处理静态资源.
9. 创建archer系统登录用户：<br/>
使用浏览器（推荐chrome或火狐）访问debug.sh里的地址：http://X.X.X.X:port/admin/sql/users/ ，如果未登录需要用到步骤7创建的admin系统用户来登录。<br/>
点击右侧Add users，用户名密码自定义，至少创建一个工程师和一个审核人（步骤7创建的用户也可以登录）后续新的工程师和审核人用户请用LDAP导入sql_users表或django admin增加<br/>
10. 配置主库地址：<br/>
使用浏览器访问http://X.X.X.X:port/admin/sql/master_config/ ，点击右侧Add master_config<br/>
这一步是为了告诉archer你要用inception去哪些mysql主库里执行SQL，所用到的用户名密码、端口等。<br/>
11. 正式访问：<br/>
以上步骤完毕，就可以使用步骤9创建的用户登录archer系统啦, 首页地址 http://X.X.X.X:port/<br/>

### 系统展示截图：
1. 用户登录页：<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/login.png)<br/>
2. 自助审核SQL，提交SQL工单：<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/submitsql.png)<br/>
3. 工单展示页：<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/allworkflow.png)<br/>
4. 版本发布提交SQL文件,查看版本工单列表，查看版本工单个详情：<br/>
版本发布页面直接读取svn目录下对应版本目录中的sql文件，供开发人员进行提交(svn路径如02Release/项目目录名/子项目目录名或版本目录名/版本目录名/)<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/versioncommit.png)<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/versionlist.png)<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/versiondetail.png)<br/>
5. mongo编码同步工单提交，批量提交，同步工单列表：<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/mongocommit.png)<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/groupsync.png)<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/mongolist.png)<br/>
6. 用户、集群、工单管理：<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/adminsqluser.png)<br/>
7. 开发工单DDL统计图表，工单个数统计图表：<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/ddlcount.png)<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/charts.png)<br/>
8. 实例DDL对比：<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/instancediff.png)<br/>

### 部分小问题解决办法：
1. 报错：<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/bugs/bug1.png)&nbsp;
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/bugs/bug2.png)<br/>
原因：python3的pymysql模块会向inception发送SHOW WARNINGS语句，导致inception返回一个"Must start as begin statement"错误被archer捕捉到报在日志里.<br/>
解决：如果实在忍受不了，请修改/path/to/python3/lib/python3.4/site-packages/pymysql/cursors.py:338行，将self._show_warnings()这一句注释掉，换成pass，如下：<br/>
![image](https://github.com/gitjacky/archer/blob/master/archer-master/screenshots/bugs/bug3.png)
