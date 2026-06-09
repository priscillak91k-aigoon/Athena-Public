#!/usr/bin/env python3
"""
Hawkeye v5.0 OCR & High-Resolution Visual Tiling Engine
Renders CAD plan sheets at high resolution and slices them into VLM-digestible tiles.
Extracts vector text and geometries to align coordinate systems.
"""

import os
import sys
import json
import fitz  # PyMuPDF
from PIL import Image
from pathlib import Path

class HawkeyeVisualParser:
    def __init__(self, pdf_path: str, output_dir: str = "tmp_pdf_analysis"):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def render_and_tile_page(self, page_num: int, dpi: int = 300, tile_size: int = 1024, overlap: int = 100):
        """
        Renders a page at high DPI and slices it into overlapping tiles for VLM processing.
        Saves tiles and returns metadata.
        """
        doc = fitz.open(self.pdf_path)
        if page_num < 0 or page_num >= len(doc):
            raise IndexError(f"Page number {page_num} out of bounds.")
            
        page = doc[page_num]
        
        # Render high DPI image
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # Convert to PIL Image
        img_path = self.output_dir / f"page_{page_num + 1}_full.png"
        pix.save(str(img_path))
        img = Image.open(img_path)
        width, height = img.size
        
        tiles = []
        # Tiling coordinates
        x = 0
        while x < width:
            y = 0
            while y < height:
                x_end = min(x + tile_size, width)
                y_end = min(y + tile_size, height)
                
                # Crop tile
                tile = img.crop((x, y, x_end, y_end))
                tile_name = f"page_{page_num + 1}_tile_{x}_{y}.png"
                tile_path = self.output_dir / tile_name
                tile.save(tile_path)
                
                tiles.append({
                    "tile_path": str(tile_path),
                    "coordinates": {
                        "x_start": x,
                        "y_start": y,
                        "x_end": x_end,
                        "y_end": y_end
                    }
                })
                
                if y_end == height:
                    break
                y += tile_size - overlap
            if x_end == width:
                break
            x += tile_size - overlap
            
        return {
            "page": page_num + 1,
            "dpi": dpi,
            "full_dimensions": {"width": width, "height": height},
            "tiles": tiles
        }

    def extract_vector_elements(self, page_num: int):
        """
        Extracts vector elements (text, lines, rects) with exact canvas coordinates.
        This provides the visual/textual coordinate alignment layer.
        """
        doc = fitz.open(self.pdf_path)
        page = doc[page_num]
        
        # Extract text blocks with coordinates
        text_instances = []
        for text_page in page.get_text("blocks"):
            x0, y0, x1, y1, text, block_no, block_type = text_page
            text_instances.append({
                "text": text.strip(),
                "bbox": [x0, y0, x1, y1],
                "block_no": block_no,
                "type": "text"
            })
            
        # Extract drawings (lines, rectangles, paths)
        drawings = []
        for draw in page.get_drawings():
            # Standardize draw primitives
            drawings.append({
                "type": draw["type"],
                "rect": [draw["rect"].x0, draw["rect"].y0, draw["rect"].x1, draw["rect"].y1],
                "color": draw["color"],
                "fill": draw["fill"],
                "width": draw["width"]
            })
            
        return {
            "page": page_num + 1,
            "text_blocks": text_instances,
            "vector_drawings": drawings[:500]  # Cap to prevent giant payloads
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hawkeye_v5_ocr.py <path_to_pdf>")
        sys.exit(1)
        
    parser = HawkeyeVisualParser(sys.argv[1])
    # Test on page 1
    print(f"Parsing page 1 of {sys.argv[1]}...")
    metadata = parser.render_and_tile_page(0, dpi=300, tile_size=1024)
    vectors = parser.extract_vector_elements(0)
    
    # Save a report
    output_report = parser.output_dir / "page_1_analysis.json"
    with open(output_report, 'w', encoding='utf-8') as f:
        json.dump({"metadata": metadata, "vectors": vectors}, f, indent=2)
    print(f"Done. Analysis saved to {output_report}")
