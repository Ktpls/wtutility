import requests
import http
import time
def get_web_server_time(host_URL, year_str='-', time_str=':'):
       '''
       获取网络时间，需要的时间会比较长，个别电脑上可能会出现不兼容现象
       :param host_URL: 目标网址，如：https://www.baidu.com/
       :param year_str: 年份中间的间隔字符，如：2019-11-22
       :param time_str: 小时和分钟中将的间隔字符，如：12:30:59
       :return: 返回时间字符串，如：2019-11-22 12:30:59
       '''
       conn = http.client.HTTPConnection(host_URL)
       conn.request("GET", "/")
       r = conn.getresponse()
       # r.getheaders() #获取所有的http头
       ts = r.getheader('date')  # 获取http头date部分
       print(ts)
       # 将GMT时间转换成北京时间
       ltime = time.strptime(ts[5:25], "%d %b %Y %H:%M:%S")
       print(ltime)
       ttime = time.localtime(time.mktime(ltime) + 8 * 60 * 60)
       print(ttime)
       year_out = "{}{}{:0>2}{}{:0>2}".format(ttime.tm_year, year_str, ttime.tm_mon, year_str, ttime.tm_mday)
       time_out = "{:0>2}{}{:0>2}{}{:0>2}".format(ttime.tm_hour, time_str, ttime.tm_min, time_str, ttime.tm_sec)
 
       output_str = year_out + " " + time_out
       print("目标网址={} 的网络时间={}".format(host_URL, output_str))
 
       print("return 时间={}".format(output_str))
       return output_str

print(get_web_server_time('www.baidu.com'))