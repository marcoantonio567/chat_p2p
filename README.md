# chat_p2p

Simple TCP chat where one node becomes the server and other nodes connect as clients.

The scripts in [chat_p2p](file:///c:/Users/marco/Desktop/update_repositorio/chat_p2p/chat_p2p) use Python sockets + threads:
- The first instance that cannot connect to any known peer starts a server on port `10000`.
- Any instance that successfully connects becomes a client and sends messages to the server.
- The server broadcasts received messages to all connected clients.

## Requirements

- Python 3.x
- Windows / Linux / macOS

No external dependencies.

## Run

From the repository root:

```bash
python chat_p2p/base.py
```

Type messages and press Enter to send.

## Connect from another machine

1. Pick one machine to be the server.
2. On the client machine, edit `p2p.peers` to point to the server IP.

Example (in [base.py](file:///c:/Users/marco/Desktop/update_repositorio/chat_p2p/chat_p2p/base.py)):

```python
class p2p:
    peers = ['192.168.0.10']
```

Then run:

```bash
python chat_p2p/base.py
```

## Notes / limitations

- Port is fixed at `10000` in the scripts.
- You cannot run multiple instances on the same machine without changing the port, because they all bind to `0.0.0.0:10000`.
- Files `cliente1.py`, `cliente2.py`, `cliente3.py`, and `chatp2p_v2.py` currently contain the same logic as `base.py`.
