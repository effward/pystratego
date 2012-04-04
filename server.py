import network_server

def main():
	network = network_server.EchoComponent('pystratego.andrew-win7', 'hello123', 'andrew-win7', '5275', 'lobby@stratego.andrew-win7', 'Admin', 'stratego.andrew-win7', get='all')
	print("Done")


if __name__ == '__main__': main()