from docling.document_converter import ConversionResult
import json
from pypdf import PdfReader
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph


# PPTX PART
def extract_group(element_id, element_type, groups, texts, pictures, tables):
    element = groups[element_id]
    children = element["children"]
    group_content = ""
    for child in children:
        child_ref = child["$ref"]
        [_, child_type, child_id] = child_ref.split("/")
        child_content = extract_content(int(child_id), child_type, groups, texts, pictures, tables)
        group_content += "\n" + child_content
    return group_content

def extract_text(element_id, element_type, groups, texts, pictures, tables):
    element = texts[element_id]
    text_content = element["text"]
    return text_content

def extract_picture(element_id, element_type, groups, texts, pictures, tables):
    return "image"

def extract_table(element_id, element_type, groups, texts, pictures, tables):
    element = tables[element_id]
    table_grid = element["data"]["grid"]
    table_content = ""
    merged_cells = set()
    current_merged_cell = None
    for row in table_grid:
        above_line = ""
        row_line = ""
        merged_cells_per_row = set()

        for cell in row:
            cell["text"] = cell["text"].replace("\n", "  ")
            if cell["row_span"] != 1 or cell["col_span"] != 1:
                current_merged_cell = str(cell["start_row_offset_idx"]) + "-" + str(cell["end_row_offset_idx"]) + "-" + str(cell["start_col_offset_idx"]) + "-" + str(cell["end_col_offset_idx"])
                if current_merged_cell not in merged_cells:
                    row_line += "| " +  cell["text"] + " "
                    above_line += "-" * (len(cell["text"]) + 3)
                    merged_cells.add(current_merged_cell)
                    merged_cells_per_row.add(current_merged_cell)
                elif current_merged_cell not in merged_cells_per_row:
                    row_line += "| " + " " * len(cell["text"]) + " "
                    above_line += " " * (len(cell["text"]) + 3)
                    merged_cells_per_row.add(current_merged_cell)
                else: 
                    row_line += " "
                    above_line += " "
            else:
                row_line += "| " +  cell["text"] + " "
                above_line += "-" * (len(cell["text"]) + 3)
        table_content += "\n" + above_line + "\n" + row_line + " |"
    return table_content


def extract_content(element_id, element_type, groups, texts, pictures, tables):
    if element_type == "groups":
        return extract_group(element_id, element_type, groups, texts, pictures, tables)
    elif element_type == "texts":
        return extract_text(element_id, element_type, groups, texts, pictures, tables)
    elif element_type == "pictures":
        return extract_picture(element_id, element_type, groups, texts, pictures, tables)
    elif element_type == "tables":
        return extract_table(element_id, element_type, groups, texts, pictures, tables)


def convert_pptx(result: ConversionResult):
    formatted_presentation = result.document.export_to_dict()
    body_elements = formatted_presentation["body"]["children"]
    groups = formatted_presentation["groups"]
    texts = formatted_presentation["texts"]
    pictures = formatted_presentation["pictures"]
    tables = formatted_presentation["tables"]

    slides = []

    for element in body_elements:
        element_ref = element["$ref"]
        [_, element_type, element_id] = element_ref.split("/")
        slide_content = extract_content(int(element_id), element_type, groups, texts, pictures, tables)
        slides.append(slide_content)
    return slides


# DOCX PART

def is_list_paragraph(paragraph):
    return paragraph.style.name.lower().startswith("list")

def iter_block_items(parent):
    """
    Generează elementele (paragrafe și tabele) în ordinea în care apar în document.
    """
    for child in parent.element.body.iterchildren():
        if child.tag.endswith('}p'):
            yield Paragraph(child, parent)
        elif child.tag.endswith('}tbl'):
            yield Table(child, parent)


def convert_docx(result, blocks_per_chunk=4):
    doc = Document(result)
    chunks = []
    current_chunk = ""
    block_count = 0

    buffer_list = []  # temporar pentru liste continue

    def flush_list():
        nonlocal current_chunk
        if buffer_list:
            current_chunk += "".join(buffer_list) + "\n"
            buffer_list.clear()

    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if not text:
                continue

            if is_list_paragraph(block):
                # Adaugă bullet manual
                buffer_list.append(f"- {text}\n")
                continue  # nu incrementăm block_count încă
            else:
                flush_list()  # dacă e sfârșit de listă, bagă-o

                current_chunk += text + "\n"
                block_count += 1

        elif isinstance(block, Table):
            flush_list()
            for row in block.rows:
                row_text = "\t".join(cell.text.strip() for cell in row.cells)
                current_chunk += row_text + "\n"
            current_chunk += "\n"
            block_count += 1

        # Dacă am ajuns la limita de blockuri
        if block_count >= blocks_per_chunk:
            flush_list()
            chunks.append(current_chunk.strip())
            current_chunk = ""
            block_count = 0

    # Ce mai rămâne
    flush_list()
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks



# PDF PART
def convert_pdf(result):
    reader = PdfReader(result)
    return [page.extract_text() for page in reader.pages]

