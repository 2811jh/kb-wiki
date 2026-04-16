#!/usr/bin/env python3
"""Convert PDF files to Markdown.

Usage:
    python convert_pdf.py <input_file> <output_md> [--images-dir <dir>]

Exit code 0 on success, non-zero on failure.
Prints JSON summary to stdout on completion.
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF
from PIL import Image


def remove_cjk_spaces(text: str) -> str:
    """Remove spurious spaces between CJK characters."""
    text = re.sub(
        r'([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])\s+([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])',
        r'\1\2', text,
    )
    # Apply twice for consecutive CJK chars separated by spaces
    text = re.sub(
        r'([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])\s+([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])',
        r'\1\2', text,
    )
    return text

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------

def validate_image(image_path: Path) -> bool:
    """Return True if *image_path* is a valid image file."""
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def extract_pdf_images(
    page,
    page_num: int,
    images_dir: Path,
    source_name: str = "image",
) -> List[Dict]:
    """Extract images from a single PDF page.

    Skips CMYK images and images smaller than 50×50 px.
    Returns a list of image-info dicts.
    """
    images_info: List[Dict] = []

    try:
        image_list = page.get_images()
        logger.debug(
            "Page %d: found %d image objects", page_num + 1, len(image_list)
        )

        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                pix = fitz.Pixmap(page.parent, xref)

                # Skip CMYK (n - alpha >= 4) and tiny images
                if pix.n - pix.alpha >= 4 or pix.width < 50 or pix.height < 50:
                    pix = None
                    continue

                seq = len(images_info) + 1
                image_filename = f"{source_name}_p{page_num + 1}_img{seq}.png"
                image_path = images_dir / image_filename

                pix.save(str(image_path))

                if validate_image(image_path):
                    images_info.append({
                        "filename": image_filename,
                        "path": str(image_path),
                        "page": page_num + 1,
                        "index": img_index,
                        "seq": seq,
                        "source_name": source_name,
                        "width": pix.width,
                        "height": pix.height,
                        "format": "png",
                    })
                else:
                    image_path.unlink(missing_ok=True)

                pix = None  # release memory

            except Exception as exc:
                logger.warning(
                    "Page %d image %d error: %s", page_num + 1, img_index, exc
                )
                continue

    except Exception as exc:
        logger.warning("Page %d image extraction failed: %s", page_num + 1, exc)

    return images_info


# ---------------------------------------------------------------------------
# Text processing
# ---------------------------------------------------------------------------

def process_pdf_text(text: str) -> List[str]:
    """Process raw PDF page text into Markdown lines.

    Applies heading detection, list detection and whitespace cleanup.
    """
    lines: List[str] = []

    text = remove_cjk_spaces(text)
    paragraphs = text.split('\n\n')

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Collapse internal newlines
        para = re.sub(r'\n+', ' ', para)
        para = re.sub(r'\s+', ' ', para)

        # Heading heuristic: short, all-uppercase or capitalised without
        # sentence-ending punctuation
        if (len(para) < 100 and
                (para.isupper() or
                 re.match(r'^[A-Z][^.!?]*$', para) or
                 re.match(r'^\d+[\.\s]+[A-Z]', para))):
            lines.append(f"## {para}")
            lines.append("")
        else:
            # List detection
            if re.match(r'^\s*[\d\w]+[.)]\s+', para) or para.startswith(('•', '-', '*')):
                if re.match(r'^\s*\d+[.)]\s+', para):
                    match = re.match(r'^\s*\d+[.)]\s+(.+)', para)
                    if match:
                        lines.append(f"1. {match.group(1)}")
                    else:
                        lines.append(para)
                else:
                    cleaned = re.sub(r'^\s*[•\-*]\s+', '', para)
                    lines.append(f"- {cleaned}")
            else:
                lines.append(para)
            lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Table extraction & conversion
# ---------------------------------------------------------------------------

def convert_pdf_table_to_markdown(
    table_data: List[List],
    page_num: int,
    table_idx: int,
) -> List[str]:
    """Convert a 2-D list of cell values to Markdown table lines."""
    if not table_data:
        return []

    markdown_table: List[str] = []

    try:
        # Filter out completely empty rows
        filtered_data: List[List[str]] = []
        for row in table_data:
            cleaned_row = []
            for cell in row:
                if cell is None:
                    cleaned_row.append("")
                else:
                    cell_str = str(cell).strip().replace('\n', ' ').replace('|', '\\|')
                    cell_str = remove_cjk_spaces(cell_str)
                    cleaned_row.append(cell_str)
            if any(cell for cell in cleaned_row):
                filtered_data.append(cleaned_row)

        if not filtered_data:
            return []

        # Normalise column count
        max_cols = max(len(row) for row in filtered_data)
        normalized_data = [row + [""] * (max_cols - len(row)) for row in filtered_data]

        # Table label
        markdown_table.append(
            f"\n**Table {table_idx + 1}** (page {page_num + 1}):\n"
        )

        # Header row
        headers = normalized_data[0]
        if all(not h or (h.isdigit() and len(h) <= 3) for h in headers):
            headers = [f"Col{i+1}" for i in range(max_cols)]
            data_rows = normalized_data
        else:
            data_rows = normalized_data[1:]

        headers = [h if h else f"Col{i+1}" for i, h in enumerate(headers)]

        markdown_table.append("| " + " | ".join(headers) + " |")
        markdown_table.append("| " + " | ".join(["---"] * len(headers)) + " |")

        for row in data_rows:
            row_display = [cell if cell else "-" for cell in row]
            markdown_table.append("| " + " | ".join(row_display) + " |")

    except Exception as exc:
        logger.warning("PDF table conversion failed: %s", exc)
        return ["*[Table parsing failed]*"]

    return markdown_table


def detect_tables_from_text(
    page_dict: Dict,
    page_num: int,
) -> Tuple[List[List[str]], List[int]]:
    """Detect borderless tables by analysing text-block positions.

    Returns ``(tables, table_block_indices)`` where *tables* is a list of
    Markdown-line lists and *table_block_indices* is the list of block indices
    that belong to detected tables.
    """
    tables: List[List[str]] = []
    table_block_indices: List[int] = []

    try:
        blocks = page_dict["blocks"]

        text_blocks: List[Dict] = []
        for block_idx, block in enumerate(blocks):
            if block.get("type") == 0:  # text block
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    if not spans:
                        continue
                    text = " ".join(
                        span.get("text", "").strip() for span in spans
                    ).strip()
                    if text:
                        bbox = line["bbox"]
                        text_blocks.append({
                            "text": text,
                            "x0": bbox[0],
                            "y0": bbox[1],
                            "x1": bbox[2],
                            "y1": bbox[3],
                            "block_idx": block_idx,
                        })

        if len(text_blocks) < 3:
            return tables, table_block_indices

        # Sort top-to-bottom
        text_blocks.sort(key=lambda b: b["y0"])

        # Group into rows by Y proximity
        rows: List[List[Dict]] = []
        current_row: List[Dict] = []
        last_y: Optional[float] = None
        y_tolerance = 5

        for tb in text_blocks:
            if last_y is None or abs(tb["y0"] - last_y) < y_tolerance:
                current_row.append(tb)
                last_y = tb["y0"]
            else:
                if current_row:
                    current_row.sort(key=lambda b: b["x0"])
                    rows.append(current_row)
                current_row = [tb]
                last_y = tb["y0"]

        if current_row:
            current_row.sort(key=lambda b: b["x0"])
            rows.append(current_row)

        if len(rows) < 2:
            return tables, table_block_indices

        # Find the most common column count
        col_counts = [len(r) for r in rows]
        most_common_cols = max(set(col_counts), key=col_counts.count)

        if col_counts.count(most_common_cols) >= len(rows) * 0.6 and most_common_cols > 1:
            table_data: List[List[str]] = []
            block_idx_set: set = set()

            for row in rows:
                if len(row) == most_common_cols:
                    table_data.append([cell["text"] for cell in row])
                    for cell in row:
                        block_idx_set.add(cell["block_idx"])

            if table_data:
                markdown_table = convert_pdf_table_to_markdown(
                    table_data, page_num, 0
                )
                if markdown_table:
                    tables.append(markdown_table)
                    table_block_indices = list(block_idx_set)
                    logger.info(
                        "Page %d: text-position table detected – %d rows × %d cols",
                        page_num + 1, len(table_data), most_common_cols,
                    )

    except Exception as exc:
        logger.warning(
            "Page %d text-based table detection failed: %s", page_num + 1, exc
        )

    return tables, table_block_indices


def extract_pdf_tables(
    page,
    page_num: int,
    page_dict: Dict,
) -> Tuple[List[Dict], List[int]]:
    """Extract tables from a PDF page using a dual strategy.

    1. Primary – ``page.find_tables()`` for standard (ruled) tables.
    2. Fallback – text-position heuristic for borderless tables.

    Returns ``(tables, table_block_indices)``.
    Each table entry is ``{'content': [...], 'bbox': tuple|None,
    'y_pos': float, 'type': 'standard'|'detected'}``.
    """
    tables: List[Dict] = []
    table_block_indices: List[int] = []
    table_count = 0

    try:
        # Strategy 1: PyMuPDF find_tables()
        tab_finder = page.find_tables()

        if tab_finder and tab_finder.tables:
            logger.info(
                "Page %d: %d standard table(s) found",
                page_num + 1, len(tab_finder.tables),
            )

            for table_idx, table in enumerate(tab_finder.tables):
                try:
                    table_data = table.extract()
                    if table_data and len(table_data) > 0:
                        md_table = convert_pdf_table_to_markdown(
                            table_data, page_num, table_count
                        )
                        if md_table:
                            bbox = table.bbox  # (x0, y0, x1, y1)
                            tables.append({
                                'content': md_table,
                                'bbox': bbox,
                                'y_pos': bbox[1],
                                'type': 'standard',
                            })
                            table_count += 1
                except Exception as exc:
                    logger.warning(
                        "Page %d standard table %d error: %s",
                        page_num + 1, table_idx + 1, exc,
                    )
                    continue

        # Strategy 2: text-position fallback
        if table_count == 0:
            logger.debug(
                "Page %d: no standard tables, trying text-position detection…",
                page_num + 1,
            )
            detected, tbi = detect_tables_from_text(page_dict, page_num)
            table_block_indices = tbi
            for dt in detected:
                tables.append({
                    'content': dt,
                    'bbox': None,
                    'y_pos': 0,
                    'type': 'detected',
                })
                table_count += 1

    except Exception as exc:
        logger.debug("Page %d table extraction failed: %s", page_num + 1, exc)

    return tables, table_block_indices


# ---------------------------------------------------------------------------
# Content ordering
# ---------------------------------------------------------------------------

def get_ordered_content_blocks(
    page_dict: Dict,
    tables: List[Dict],
    images: List[Dict],
    table_block_indices: List[int],
    img_rel: str,
) -> List[Dict]:
    """Return content blocks (text / table / image) sorted by Y-position."""
    content_blocks: List[Dict] = []

    try:
        blocks = page_dict["blocks"]
        image_idx = 0

        standard_tables = [
            t for t in tables if t.get('type') == 'standard' and t.get('bbox')
        ]
        detected_tables = [t for t in tables if t.get('type') == 'detected']

        # Insert standard tables
        for table_info in standard_tables:
            y_pos = table_info['y_pos']
            content_blocks.append({
                'type': 'table',
                'content': table_info['content'],
                'y_pos': y_pos,
                'sort_key': (y_pos, -1),
            })

        tbi_set = set(table_block_indices)
        min_tbi = min(table_block_indices) if table_block_indices else -1

        for block_idx, block in enumerate(blocks):
            block_type = block.get("type")

            if block_type == 0:  # text block
                bbox = block.get("bbox", [0, 0, 0, 0])
                y_pos = bbox[1]

                # Skip text that overlaps with a standard table
                is_in_table = False
                if standard_tables:
                    for ti in standard_tables:
                        t_bbox = ti['bbox']
                        if (bbox[0] >= t_bbox[0] - 5 and
                                bbox[2] <= t_bbox[2] + 5 and
                                bbox[1] >= t_bbox[1] - 5 and
                                bbox[3] <= t_bbox[3] + 5):
                            is_in_table = True
                            break

                if is_in_table:
                    continue

                if block_idx in tbi_set:
                    # Insert detected table at the first block position
                    if block_idx == min_tbi and detected_tables:
                        content_blocks.append({
                            'type': 'table',
                            'content': detected_tables[0]['content'],
                            'y_pos': y_pos,
                            'sort_key': (y_pos, block_idx),
                        })
                else:
                    # Normal text
                    text_parts: List[str] = []
                    for line in block.get("lines", []):
                        spans = line.get("spans", [])
                        if spans:
                            text = " ".join(
                                span.get("text", "").strip() for span in spans
                            ).strip()
                            if text:
                                text_parts.append(text)

                    if text_parts:
                        content_blocks.append({
                            'type': 'text',
                            'content': remove_cjk_spaces(" ".join(text_parts)),
                            'y_pos': y_pos,
                            'sort_key': (y_pos, block_idx),
                        })

            elif block_type == 1:  # image block
                if image_idx < len(images):
                    bbox = block.get("bbox", [0, 0, 0, 0])
                    y_pos = bbox[1]
                    img_info = images[image_idx]
                    rel_path = os.path.join(
                        img_rel, img_info['filename']
                    ).replace('\\', '/')
                    img_alt = f"{img_info.get('source_name', 'Image')}-第{img_info['page']}页图{img_info.get('seq', image_idx + 1)}"
                    content_blocks.append({
                        'type': 'image',
                        'content': f"![{img_alt}]({rel_path})",
                        'y_pos': y_pos,
                        'sort_key': (y_pos, block_idx),
                    })
                    image_idx += 1

        content_blocks.sort(key=lambda x: x['sort_key'])

    except Exception as exc:
        logger.warning("Failed to build ordered content blocks: %s", exc)

    return content_blocks


# ---------------------------------------------------------------------------
# Markdown cleanup
# ---------------------------------------------------------------------------

def clean_markdown(lines: List[str]) -> str:
    """Join *lines* into a single Markdown string, trimming excess blanks."""
    content = "\n".join(lines)
    content = re.sub(r'\n{3,}', '\n\n', content)
    stripped = [l.rstrip() for l in content.split('\n')]
    while stripped and not stripped[0].strip():
        stripped.pop(0)
    while stripped and not stripped[-1].strip():
        stripped.pop()
    return '\n'.join(stripped)


# ---------------------------------------------------------------------------
# Main conversion
# ---------------------------------------------------------------------------

def convert_pdf(input_file: str, output_md: str, images_dir: str) -> Dict:
    """Convert *input_file* (.pdf) → Markdown written to *output_md*.

    Returns a summary dict.
    """
    input_path = Path(input_file)
    output_path = Path(output_md)
    img_dir = Path(images_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    img_dir.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Relative path from output markdown to images directory
    try:
        img_rel = os.path.relpath(img_dir, output_path.parent)
    except ValueError:
        img_rel = str(img_dir)

    doc = fitz.open(str(input_path))

    # Derive clean source filename (strip bracket prefixes)
    stem = input_path.stem
    source_name = re.sub(r'\[.*?\]', '', stem).strip()
    if not source_name:
        source_name = stem

    total_pages = len(doc)
    logger.info("PDF document has %d pages", total_pages)

    markdown_content: List[str] = []
    all_images: List[Dict] = []
    total_tables = 0

    for page_num in range(total_pages):
        try:
            page = doc.load_page(page_num)

            # Cache the structured dict for the page (avoids repeated calls)
            page_dict = page.get_text("dict")

            # --- tables ---
            tables, table_block_indices = extract_pdf_tables(
                page, page_num, page_dict
            )
            total_tables += len(tables)

            # --- images ---
            page_images = extract_pdf_images(page, page_num, img_dir, source_name)
            if page_images:
                all_images.extend(page_images)

            # --- page separator ---
            if page_num > 0:
                markdown_content.append("")
                markdown_content.append("---")
                markdown_content.append("")
            markdown_content.append(f"## 第 {page_num + 1} 页")
            markdown_content.append("")

            # --- assemble content ---
            if tables:
                content_blocks = get_ordered_content_blocks(
                    page_dict, tables, page_images,
                    table_block_indices, img_rel,
                )
                for block in content_blocks:
                    if block['type'] == 'text':
                        markdown_content.append(block['content'])
                        markdown_content.append("")
                    elif block['type'] == 'table':
                        markdown_content.extend(block['content'])
                        markdown_content.append("")
                    elif block['type'] == 'image':
                        markdown_content.append(block['content'])
                        markdown_content.append("")
            else:
                # No tables – plain text + images
                text = page.get_text()
                if text.strip():
                    processed = process_pdf_text(text)
                    markdown_content.extend(processed)

                for img_info in page_images:
                    rel_path = os.path.join(
                        img_rel, img_info['filename']
                    ).replace('\\', '/')
                    img_alt = f"{source_name}-第{img_info['page']}页图{img_info.get('seq', 0)}"
                    markdown_content.append(f"![{img_alt}]({rel_path})")
                    markdown_content.append("")

        except Exception as exc:
            logger.warning("Error processing page %d: %s", page_num + 1, exc)
            continue

    doc.close()

    result_md = clean_markdown(markdown_content)

    if not result_md.strip():
        result_md = "*PDF document content is empty or cannot be parsed*"

    output_path.write_text(result_md, encoding='utf-8')

    return {
        "success": True,
        "file_type": "pdf",
        "pages": total_pages,
        "tables": total_tables,
        "images": len(all_images),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert a .pdf file to Markdown."
    )
    parser.add_argument("input_file", help="Path to the .pdf file")
    parser.add_argument("output_md", help="Path to write the resulting .md file")
    parser.add_argument(
        "--images-dir",
        default=None,
        help="Directory to save extracted images (default: same dir as output_md)",
    )
    args = parser.parse_args()

    images_dir = args.images_dir
    if images_dir is None:
        images_dir = str(Path(args.output_md).parent)

    try:
        summary = convert_pdf(args.input_file, args.output_md, images_dir)
        print(json.dumps(summary))
        return 0
    except Exception as exc:
        err = {"success": False, "error": str(exc)}
        print(json.dumps(err), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
