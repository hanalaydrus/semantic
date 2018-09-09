from server import Server
import threading

if __name__ == '__main__':
	print("1-thread active: %d" % (threading.active_count()))
	print(threading.enumerate())

	serverSemantic = Server("serverSemantic")

	serverSemantic.start()

	serverSemantic.join()
    
