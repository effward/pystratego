import network_server

def main():
	network = network_server.EchoComponent('component@localhost', 'hello123', 'localhost', '5275', 'lobby@stratego.andrew-win7', 'Admin', 'stratego.andrew-win7', get='all')
	print("Done")


if __name__ == '__main__': main()