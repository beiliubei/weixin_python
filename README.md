weixin_python
=============

使用web.py+uwsgi进行微信公众平台帐号开发

####需要安装的库
	MySQLdb
	web.py
	JenkinsAPI

####暂时实现的功能
    “addURL:+URL”
    将用户的默认Jenkins设置为URL
    “query”
    查询用户所建立的所有任务
    “addTask:+taskName(+URL)”
    建立名为taskName的任务，如用户指定了URL则将对应的JenkinsURL设为URL，否则设定为默认URL