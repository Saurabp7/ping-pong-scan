from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pytesseract
from PIL import Image
import io

app = FastAPI()

# Fixed unjumble permutation (example: [2, 5, 0, ...])
# This should reverse the fixed jumble done during SVG creation
UNJUMBLE_PERMUTATION = [2, 5, 0, 1, 4, 3, 6, 7, 9, 10, 8, 11, 13, 14, 12, 15]

# Fixed symbol positions to be removed after unjumbling
SYMBOL_POSITIONS = [3, 7, 11, 15]

def preprocess_image(image: Image.Image) -> Image.Image:
    return image.convert("L")  # Grayscale conversion (optional improvements possible)

def extract_text(image: Image.Image) -> str:
    custom_config = r'--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$█'
    text = pytesseract.image_to_string(image, config=custom_config)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    characters = ''.join(lines)
    return characters

def unjumble(text: str) -> str:
    if len(text) != 16:
        return ""
    unjumbled = [''] * 16
    for i, idx in enumerate(UNJUMBLE_PERMUTATION):
        unjumbled[idx] = text[i]
    return ''.join(unjumbled)

def remove_symbols(text: str) -> str:
    return ''.join([c for i, c in enumerate(text) if i not in SYMBOL_POSITIONS])

@app.post("/scan")
async def scan_matrix(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    image = preprocess_image(image)
    raw_text = extract_text(image)

    # Pad or trim to 16 characters
    raw_text = raw_text[:16].ljust(16, ' ')
    unjumbled = unjumble(raw_text)
    final_code = remove_symbols(unjumbled)

    return JSONResponse({"raw": raw_text, "unjumbled": unjumbled, "code": final_code})
