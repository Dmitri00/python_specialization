from server import run_server
if __name__ == "__main__":
    import sys
    host = sys.argv[1]
    port = sys.argv[2]
    run_server(host, int(port))