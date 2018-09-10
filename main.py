from server import Server
import stacktracer

if __name__ == '__main__':
	# stacktracer.trace_start("trace.html",interval=5,auto=True)

	serverSemantic = Server("serverSemantic")

	serverSemantic.start()

	serverSemantic.join()

	# stacktracer.trace_stop()
    
