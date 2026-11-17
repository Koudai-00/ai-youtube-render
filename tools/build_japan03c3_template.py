# -*- coding: utf-8 -*-
import os, runpy
from pathlib import Path
os.environ["EP_CH"] = "japan03c3"
runpy.run_path(str(Path(__file__).resolve().parent / "japan03_chapter_builder.py"), run_name="__main__")
