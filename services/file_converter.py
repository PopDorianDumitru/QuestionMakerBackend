from docling.document_converter import ConversionResult
import json
import pdfplumber

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

def convert_docx(result):
    pass

def convert_pdf(result):
    with pdfplumber.open(result) as pdf:
        pages = []
        for page in pdf.pages:
            pages.append(page.extract_text())
        return pages 