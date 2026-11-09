# -*- coding: utf-8 -*-
import os, runpy
from pathlib import Path
os.environ["EP_CH"] = "japan01c1"
runpy.run_path(str(Path(__file__).resolve().parent / "japan01_chapter_builder.py"), run_name="__main__")
