#!/usr/bin/python
#encoding=utf-8

import web
import hashlib
import urllib2
import urllib
import time
import xml.dom.minidom
import json
import urlparse
import re
import sys
from jenkinsapi.jenkins import Jenkins
reload(sys)
sys.setdefaultencoding('utf-8')

urls = (
	'/.*','index',
	)

app = web.application(urls, globals())

render = web.template.render('templates/', cache=False)
helpstr = '哈哈哈哈哈123'

class index:
	def sign(self, dic):
		signature = dic.get('signature','')
		timestamp = dic.get('timestamp','')
		nonce = dic.get('nonce','')
		echostr = dic.get('echostr','ok')
		token = 'fooying'
		checklist = [token,nonce,timestamp]
		checklist.sort()
		strs = checklist[0]+checklist[1]+checklist[2]
		sha1result = hashlib.sha1(strs).hexdigest()
		if sha1result == signature:
			return echostr
		else:
			return 'fooying'

	def simshttp(self, text):
		text = urllib.quote(text.encode('utf-8'))
		url = 'http://www.simsimi.com/func/req?lc=ch&msg=%s'%text
		req = urllib2.Request(url)
		req.add_header('Referer','http://www.simsimi.com/talk.htm?lc=ch')
		req.add_header('User-Agent','Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')
		req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
		req.add_header('Cookie','JSESSIONID=8DBCA2CEF308AB340641266203B30D8F')
		res = urllib2.urlopen(req)
		html = res.read()
		res.close()
		return json.loads(html)

	def scanv(self, url):
		url = 'http://www.anquan.org/seccenter/search/%s'%url
		req = urllib2.Request(url)
		req.add_header('User-Agent','Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')
		res = urllib2.urlopen(req)
		html = res.read()
		res.close()
		score_regex = '''<span\sclass="score">(\d*?)</span>'''
		title_regex = '''<span\sclass="pull-left "\sid="site-title"\stitle="(.*?)">'''
		safe_regex = '''<div\sclass="level-title\ssafe">(.*?)</div>'''
		mal_regex = '''<div\sclass="level-title\sdanger">(.*?)</div>'''
		sus_regex = '''<div\sclass="level-title\ssuspicious">(.*?)</div>'''
		result = {'score':'unknown','title':'','safe':'未知网站'}
		score = re.search(score_regex, html)
		if score:
			result['score'] = score.group(1)
		title = re.search(title_regex, html)
		if title:
			result['title'] = title.group(1)
		safe = re.search(safe_regex, html)
		if safe:
			result['safe'] = '安全网站'
		mal = re.search(mal_regex, html)
		if mal:
			result['safe'] = '危险网站'
		sus = re.search(sus_regex, html)
		if sus:
			result['safe'] = '存在被黑客入侵风险'
		return result

	def get_woobug(self, text):
		if '@' not in text:
			url = 'http://api.wooyun.org/bugs/limit/1'
		elif '提交' in text:
			url = 'http://api.wooyun.org/bugs/submit/limit/1'
		elif '确认' in text:
			url = 'http://api.wooyun.org/bugs/confirm/limit/1'
		elif '公开' in text:
			url = 'http://api.wooyun.org/bugs/public/limit/1'
		elif '待认' in text:
			url = 'http://api.wooyun.org/bugs/unclaim/limit/1'
		req = urllib2.Request(url)
		req.add_header('User-Agent','Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')
		res = urllib2.urlopen(req)
		html = res.read()
		res.close()
		status= {
			'0':'待厂商确认处理',
			'1':'厂商已经确认',
			'2':'漏洞通知厂商但厂商忽略',
			'3':'未联系到厂商或厂商忽略',
			'4':'正在联系厂商并等待认领',
		}
		bug = json.loads(html)[0]
		msg = '漏洞标题:%s\n漏洞状态:%s\n用户定义危害等级:%s\n厂商定义危害等级:%s\n厂商RANK:%s\n发布日期:%s\n漏洞链接:%s\n'%(bug['title'],status[bug['status']],bug['user_harmlevel'],bug['corp_harmlevel'],bug['corp_rank'],bug['date'],bug['link'])
		return msg

	def faceplus(self, imgurl):
		url = 'https://api.faceplusplus.com/detection/detect?url=%s&api_secret=%s&api_key=%s'%(imgurl,"Th-wQ5pWZS07Zx7mYyLOmPjfY2i9vHVs","18e024e52967e5f6d5104dcb54314f10")
		req = urllib2.Request(url)
		req.add_header('User-Agent','Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')
		res = urllib2.urlopen(req)
		html = res.read()
		res.close()
		faces = json.loads(html)
		xingbie = {
			'Male':'男',
			'Female':'女',
		}
		zhongzu ={
			'White':'白种人',
			'Asian':'黄种人',
			'Black':'黑人',
		}
		msg = ''
		i = 0
		for fa in faces['face']:
			i += 1
			f = fa['attribute']
			xb = xingbie[f['gender']['value']]
			nl = f['age']['value']
			wc = f['age']['range']
			zz = zhongzu[f['race']['value']]
			msg = msg +'人脸%s:\n性别:%s\n年龄:%s(误差:%s)\n种族:%s\n'%(i,xb,nl,wc,zz)
		return msg

	def ifurl(self, text):
		text = text.strip()
		if not '.' in text:
			return False
		elif text.startswith(('http://','https://')):
			return True
		else:
			path = urlparse.urlparse(text).path
			if text.split('/')[0] == path:
				return True
			else:
				return False

	def post_text(self, msg, FromUserName, ToUserName):
		post = {}
		post['ToUserName'] = FromUserName
		post['FromUserName'] = ToUserName
		post['CreateTime'] = time.time()
		post['MsgType'] = 'text'
		post['Content'] = msg
		post['FuncFlag'] = 0
		web.header('Content-Type', 'text/xml')
		return render.post_text(post)

	def check_text(self, text,FromUserName):
		text = text.strip()
		try:
			db = web.database(dbn='mysql',db='wx',host='pi.iccapp.com',port=8306,user='root',pw='',)
		except:
			return 'Cannot connect to database'
		if text == 'test':
			msg = 'test too！!'
		elif re.findall(re.compile(r'addURL:'),text):
			expression = r'addURL:\s*([a-zA-z]+://[^s]*)'
			expc = re.compile(expression)
			result = re.findall(expc,text)
			if result:
				try:
					if not db.select('wx_user_url',where='openId = $FromUserName',vars=locals()):
						try:
							db.insert('wx_user_url',openId=FromUserName,URL=result[0])
						except:
							msg = 'Database Error'
					else:
						try:
							db.update('wx_user_url', where='openId = $FromUserName',vars=locals(),URL = result[0])
							msg = 'The default Jenkins URL is set to ' + result[0]
						except:
							msg = 'Database Error'
				except:
					msg = 'Database Error'
		elif re.findall(re.compile(r'addTask:'),text):
			complexexp = r'addTask:\s*([^\s]+)\s*([^\s]+):([^\s]+)@([a-zA-z]+://[^s]*)'
			expc = re.compile(complexexp)
			result = expc.findall(text)
			if result:
				if len(result[0]) == 4:
					try:
						db.insert('wx_user',openId=FromUserName,taskName=result[0][0],JenkinsURL=result[0][3],username=result[0][1],pw=result[0][2])
						msg = 'Task name is ' + result[0][0] + '\nURL is ' + result[0][3]
						return msg
					except:
						msg = 'Insert error'
						return msg
			expression = r'addTask:\s*([^\s]+)\s*([a-zA-z]+://[^s]*)*'
			expc = re.compile(expression)
			result = re.findall(expc,text)
			if result:
				if result[0][1]:
					try:
						db.insert('wx_user',openId=FromUserName,taskName=result[0][0], JenkinsURL=result[0][1])
						msg = 'Task name is ' + result[0][0] +'\n URL is ' + result[0][1]
					except:
						msg = 'Insert error'
				else:
					try:
						url = list(db.select('wx_user_url',what='URL',where='openId = $FromUserName',vars=locals()))
						db.insert('wx_user',openId=FromUserName,taskName=result[0][0],JenkinsURL=url[0].URL)
						msg = 'Task name is ' + result[0][0] + '\n URL is ' + url[0].URL
					except:
						msg = 'Insert error'
		elif re.findall(re.compile(r'build:'),text):
			expression = r'build:\s*([^\s]+)'
			expc = re.compile(expression)
			result = re.findall(expc,text)
			if result:
				taskName = result[0]
				try:
					res = db.select('wx_user',where='openId = $FromUserName and taskName = $taskName',vars=locals())
					j = Jenkins('http://pi.iccapp.com:58082')
					for item in res:
						j.build_job(jobname=item.taskName)
				except:
					msg = 'select error'
		elif text == 'query':
			try:
				res = db.select('wx_user',where='openId = $FromUserName',vars = locals())
				msg = 'Here is your task:\n'
				for item in res:
					msg = msg + '%d'%item.taskId + ' ' + item.taskName + ' ' + item.JenkinsURL + '\n'
			except:
				msg = 'Error'
		elif text == '#help#':
			msg = 'is this true'
		elif text.startswith('#漏洞') and text.endswith('#'):
			msg = self.get_woobug(text)
		elif self.ifurl(text):
			result = self.scanv(text.strip())
			msg = '网址:[%s]\n标题:%s\n检测分数:%s\n安全检测:%s\n该检测结果由安全联盟(http://www.anquan.org)提供技术支持\n'%(text.strip(),result['title'],result['score'],result['safe'])
		else:
			ret = self.simshttp(text)
			if ret:
				msg = ret['response']
			else:
				msg = '输入#help#查看帮助\n'+helpstr
		return msg

	def GET(self):
		params = web.input()
		return self.sign(params)

	def POST(self):
		params = web.input()
		data= web.data()
		sign = self.sign(params)
		if sign != 'fooying':
			dom = xml.dom.minidom.parseString(data)
			root = dom.documentElement
			ToUserName = root.getElementsByTagName('ToUserName')[0].childNodes[0].data
			FromUserName = root.getElementsByTagName('FromUserName')[0].childNodes[0].data
			CreateTime = root.getElementsByTagName('CreateTime')[0].childNodes[0].data
			MsgType = root.getElementsByTagName('MsgType')[0].childNodes[0].data
			MsgId = root.getElementsByTagName('MsgId')[0].childNodes[0].data
			if MsgType == 'text':
				Content = root.getElementsByTagName('Content')[0].childNodes[0].data
				msg = self.check_text(Content,FromUserName)
			elif MsgType == 'image':
				PicUrl = root.getElementsByTagName('PicUrl')[0].childNodes[0].data
				msg = self.faceplus(PicUrl)
			return self.post_text(msg, FromUserName, ToUserName)

if __name__ == "__main__":
	app.run()
else:
	application = app.wsgifunc()

