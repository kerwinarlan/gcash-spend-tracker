#!/bin/bash
# Local TikTok Shop tracker: SMS capture loop + localhost web server.
# All data stays on this Mac. Usage: ./tracker.sh [start|stop]
cd "$(dirname "$0")"

start_piece() {
  local name=$1 cmd=$2
  if [ -f "$name.pid" ] && kill -0 "$(cat "$name.pid")" 2>/dev/null; then
    echo "$name already running (pid $(cat "$name.pid"))"
  else
    nohup bash -c "$cmd" >> "$name.log" 2>&1 &
    echo $! > "$name.pid"
    echo "$name started (pid $!)"
  fi
}

case "${1:-start}" in
  start)
    start_piece capture 'while true; do python3 capture.py; sleep 300; done'
    start_piece serve 'python3 -m http.server 8901 --bind 127.0.0.1 --directory .'
    echo "open http://127.0.0.1:8901/tracker.html"
    ;;
  stop)
    for name in capture serve; do
      if [ -f "$name.pid" ] && kill -0 "$(cat "$name.pid")" 2>/dev/null; then
        kill "$(cat "$name.pid")" && rm -f "$name.pid" && echo "$name stopped"
      fi
    done
    ;;
  *) echo "usage: $0 [start|stop]"; exit 1 ;;
esac
