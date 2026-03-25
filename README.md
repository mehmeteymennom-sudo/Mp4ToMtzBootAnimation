# Mp4 → MTZ Boot Animation Creator

**A tool to convert short videos into Android MTZ boot animations.**  

---

## Features

- Extracts a video **frame by frame** to create boot animations  
- Creates `part0` folder and `desc.txt` for **proper Android bootanimation format**  
- Generates ZIP files and optionally embeds them into **MTZ format**  
- **Python GUI:** Select video, save as ZIP or MTZ  
- **EXE version:** No need for Python libraries, runs standalone  

---

## Requirements (Python version)

- `PyQt5`  
- `opencv-python`  
- Standard Python libraries: `os`, `shutil`, `zipfile`  

> **Note:** Python version requires installing these libraries. EXE version works without extra dependencies.

The exe link :https://drive.google.com/file/d/1yfrdPErSsZASegOUR3Q3OFvzGD5X2uQO/view?usp=sharing

---

## Usage

1. **For Python version:**  
```bash
python Mp4ToMtz.py
