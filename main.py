"""
main.py
Entry point for the Laptop Price Tracker.
"""
#test
import sys
import os

#make sure sibling packages are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gui.gui import launch

if __name__ == "__main__":
    launch()
