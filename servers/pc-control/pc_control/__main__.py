"""Entry point for the PC Control server."""

from pc_control.server import start_server

def main() -> None:
    start_server()

if __name__ == "__main__":
    main()
