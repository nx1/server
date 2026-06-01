#!/bin/bash

# Simple wrapper script to launch real-time bandwidth monitors
clear
echo "============================================="
echo "       nx1 Server Bandwidth Monitor          "
echo "============================================="
echo "Choose a tool to monitor your connection:"
echo ""
echo "1) nload - Real-time ASCII upload/download graph"
echo "2) iftop - Live connection speed breakdown by IP address (requires sudo)"
echo "3) Exit"
echo "============================================="
echo -n "Select option [1-3]: "
read -r opt

case $opt in
  1)
    if command -v nload >/dev/null 2>&1; then
      nload
    else
      echo "Error: 'nload' is not installed."
    fi
    ;;
  2)
    if command -v iftop >/dev/null 2>&1; then
      echo "Launching iftop... (elevating privileges with sudo)"
      sudo iftop
    else
      echo "Error: 'iftop' is not installed."
    fi
    ;;
  3)
    echo "Exiting monitor."
    exit 0
    ;;
  *)
    echo "Invalid option."
    exit 1
    ;;
esac
