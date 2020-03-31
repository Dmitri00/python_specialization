from server import run_server
if __name__ == "__main__":
    import sys
    port = sys.argv[1]
    run_server('127.0.0.1', int(port))