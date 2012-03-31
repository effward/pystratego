import network_server

def main():
	network = network_server.EchoComponent('component@localhost', 'hello123', 'localhost', '5275')
	network.connect()
	network.process(block=True)
	print("Done")


if __name__ == '__main__': main()