# Extraction
# LabelAI — Diagram Label & Keyword Extractor

An AI-powered tool that extracts labels from science diagrams and automatically generates synonyms, alternate names, chemical formulas, and abbreviations for each label.

Upload any handwritten or printed diagram — biology, chemistry, physics, or maths — and get a full keyword set for every label in seconds.

---

## What It Does

- Extracts text labels from uploaded diagram images using OCR
- Merges nearby words into correct multi-word labels (e.g. "Outer" + "Membrane" → "Outer Membrane")
- Preserves chemical formulas and subscripts (H₂O → H2O, CO₂ → CO2)
- Generates synonyms, alternate names, formulas, and abbreviations for each label
- Lets you edit, add, or delete labels and keywords
- Saves diagrams for later use
- Uses Claude AI (optional) for labels not in the built-in dictionary

---

## Project Structure

```
extraction/
│
├── app.py                      ← Flask backend (main entry point)
│
├── static/
│   ├── script.js               ← Frontend logic
│   └── style.css               ← UI styling
│
├── templates/
│   └── index.html              ← Main UI page
│
├── uploads/
│   └── diagram_uploads/        ← Uploaded images stored here
│
├── utils/
│   ├── __init__.py             ← Empty file (makes utils a package)
│   ├── preprocess.py           ← Image preprocessing for better OCR
│   ├── ocr.py                  ← Text extraction using EasyOCR
│   ├── normalize.py            ← Text normalization for matching
│   ├── keyword_generator.py    ← Synonym & keyword generation
│   ├── build_keywords.py       ← Builds keyword dictionary from labels
│   └── database.py             ← Saves/loads diagrams and label configs
│
├── answer_keywords.json        ← Active keyword database (auto-generated)
├── diagrams_store.json         ← Saved diagram records (auto-generated)
├── label_config.json           ← Label editor config (auto-generated)
│
├── requirements.txt            ← Python dependencies
└── README.md                   ← This file
```

> The three `.json` files are created automatically when you first run the app. You do not need to create them manually.

---

## Requirements

### System Requirements

- Python 3.8 or higher
- macOS, Windows, or Linux
- At least 2GB free disk space (EasyOCR downloads a ~100MB model on first run)

### Python Libraries

```
flask
opencv-python
easyocr
numpy
rapidfuzz
requests
```

---

## Installation

### Step 1 — Clone or download the project

```bash
cd ~/Desktop
# If using git:
git clone <your-repo-url> extraction
cd extraction

# Or just navigate to your project folder:
cd /path/to/extraction
```

### Step 2 — Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Mac / Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` appear in your terminal prompt.

### Step 3 — Install dependencies

```bash
pip install flask opencv-python easyocr numpy rapidfuzz requests
```

Or if you have a `requirements.txt`:

```bash
pip install -r requirements.txt
```

> **Note:** EasyOCR is a large package (~500MB with dependencies including PyTorch). Installation may take 5–10 minutes depending on your internet speed.

### Step 4 — Create the `__init__.py` file

This file tells Python that `utils/` is a package. Create it if it doesn't exist:

```bash
touch utils/__init__.py
```

On Windows:
```bash
type nul > utils\__init__.py
```

### Step 5 — (Optional) Set up Claude AI API key

The built-in dictionary covers 150+ science terms. For labels not in the dictionary, you can enable Claude AI by setting your API key.

Get a free API key at: **console.anthropic.com**

**Mac / Linux — set for current session:**
```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
```

**Mac / Linux — set permanently:**
```bash
echo 'export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx' >> ~/.zshrc
source ~/.zshrc
```

**Windows:**
```bash
set ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
```

---

## Running the App

```bash
python app.py
```

You should see:

```
Using CPU. Note: This module is much faster with a GPU.
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Open your browser and go to:

```
http://127.0.0.1:5000
```

---

## How to Use

### 1. Upload a Diagram
- Enter a name for your diagram (e.g. "Human Eye", "Photosynthesis")
- Drag and drop an image or click Browse
- Click **Extract Labels**
- Wait for OCR to finish (first run is slow — EasyOCR loads its model)

### 2. Edit Labels & Keywords
- The label editor appears automatically after extraction
- Each label shows its synonyms and alternate names
- Click **✨** on any label to generate AI keywords for that label
- Click **✨ AI All** to generate keywords for all labels at once
- Click **+ Add Label** to manually add a missed label
- Click **✕** on any label to delete it
- Click **💾 Save** when done

### 3. Saved Diagrams
- All uploaded diagrams are saved automatically
- Click **Open** to reload a saved diagram into the editor
- Click **🗑** to permanently delete a diagram

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'requests'`**
```bash
pip install requests
```

**`ModuleNotFoundError: No module named 'utils.keyword_generator'`**

Make sure `utils/__init__.py` exists:
```bash
touch utils/__init__.py
```

**`No labels detected`**

- Use a clearer, higher-resolution image
- Make sure the diagram has visible text labels
- Try a printed diagram instead of handwritten for best results

**EasyOCR takes very long on first run**

This is normal. EasyOCR downloads its recognition model (~100MB) the first time. Subsequent runs are fast.

**Port already in use**

Change the port in `app.py`:
```python
app.run(debug=True, port=5001)
```
Then open `http://127.0.0.1:5001`

**To stop the server:** press `Ctrl + C` in the terminal.

---

## Supported Diagram Types

| Subject | Examples |
|---|---|
| Biology | Eye, Heart, Neuron, Leaf, Flower, Plant Cell, Animal Cell, Photosynthesis |
| Chemistry | Molecules, Reactions, Periodic elements, Lab apparatus |
| Physics | Circuits, Force diagrams, Wave diagrams, Motion |
| Maths | Geometry, Graphs, Statistical diagrams |
| Any other | The built-in dictionary + Claude AI handle most science labels |

---

## Built With

| Tool | Purpose |
|---|---|
| Flask | Python web framework |
| EasyOCR | Handwritten text recognition |
| OpenCV | Image preprocessing |
| Claude AI (Haiku) | AI keyword generation |
| NumPy | Image array processing |

---

## License

This project is built for educational purposes as a college mini project.
