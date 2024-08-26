#✓使用globalsys模块提供各模块对整个系统的交互
##使用globalsys内的类WtUtilityModule定义各模块接口
以便于装载卸载模块，现在存在问题，例如重启时，会因为仍有engineman线程运行中，未收到终止命令，而不能退出
#✓使用包装了logging的新输出系统规范化全系统输出形式
便于输出调试信息
#wtdmp
##seperate different and independent logics into different functions
##do them in parallel
##seperate computation logic and message making up logic
#afm
##add "accept current map" function
###which is, process accept message during network canceled period, reconnect network and exit afm
###use messaged thread instead of stoppable thread