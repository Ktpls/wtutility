import time, threading

num = 0
stoptask=False

def show():
    while(not stoptask):
        print(num)
        time.sleep(0.5)

def add():
    global num,stoptask
    while(num<100):
        num=num+1
        time.sleep(0.1)
    stoptask=True

# t1 = threading.Thread(target=show, args=())
# t2 = threading.Thread(target=add, args=())
# t1.start()
# t2.start()
# t1.join()
# t2.join()

t1 = threading.Thread(target=show, args=())
t1.start()
add()