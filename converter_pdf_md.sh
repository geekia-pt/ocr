#!/bin/bash
#
# Script de Conversão PDF para Markdown - Versão macOS
# Converte todos os PDFs de uma pasta para arquivos .md
#
# Uso: ./converter_pdf_md.sh "/Users/macbook_pro/Desktop/PDF TO MD"
#

set -e  # Para em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   PDF para Markdown - Conversor Automático${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

# Verifica se o caminho foi fornecido
if [ -z "$1" ]; then
    echo -e "${RED}❌ Erro: Forneça o caminho da pasta com os PDFs${NC}"
    echo -e "${YELLOW}Uso: $0 \"/caminho/para/pasta\"${NC}"
    echo -e "${YELLOW}Exemplo: $0 \"/Users/macbook_pro/Desktop/PDF TO MD\"${NC}"
    exit 1
fi

PDF_DIR="$1"

# Verifica se a pasta existe
if [ ! -d "$PDF_DIR" ]; then
    echo -e "${RED}❌ Erro: A pasta '$PDF_DIR' não existe${NC}"
    exit 1
fi

# Verifica se o Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não está instalado${NC}"
    echo -e "${YELLOW}Instale com: brew install python3${NC}"
    exit 1
fi

# Verifica se PyMuPDF está instalado
echo -e "${YELLOW}🔍 Verificando dependências...${NC}"
if ! python3 -c "import fitz" 2>/dev/null; then
    echo -e "${YELLOW}📦 Instalando PyMuPDF...${NC}"
    pip3 install PyMuPDF --quiet
    echo -e "${GREEN}✅ PyMuPDF instalado${NC}"
else
    echo -e "${GREEN}✅ PyMuPDF já instalado${NC}"
fi

# Cria o script Python inline
PYTHON_SCRIPT=$(cat <<'PYTHON_EOF'
import sys
import os
import re
from pathlib import Path
import fitz  # PyMuPDF

class PDFToMarkdownConverter:
    def __init__(self):
        self.current_doc_title = ""

    def is_heading(self, text, font_size, avg_font_size):
        if not text or len(text.strip()) == 0:
            return False
        text = text.strip()
        if font_size > avg_font_size * 1.2:
            return True
        if len(text) < 60:
            upper_count = sum(1 for c in text if c.isupper())
            alpha_count = sum(1 for c in text if c.isalpha())
            if alpha_count > 0 and upper_count / alpha_count > 0.7:
                return True
        return False

    def clean_text(self, text):
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()

    def extract_text_with_formatting(self, page):
        blocks = []
        text_dict = page.get_text("dict")
        for block in text_dict["blocks"]:
            if block["type"] == 0:
                for line in block["lines"]:
                    line_text = ""
                    font_sizes = []
                    for span in line["spans"]:
                        line_text += span["text"]
                        font_sizes.append(span["size"])
                    if line_text.strip():
                        avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12
                        blocks.append({
                            "text": line_text,
                            "font_size": avg_font_size,
                            "bbox": line["bbox"]
                        })
        return blocks

    def format_as_markdown(self, blocks, page_num, total_pages):
        if not blocks:
            return ""
        avg_font_size = sum(b["font_size"] for b in blocks) / len(blocks)
        markdown_lines = []
        if total_pages > 1:
            if page_num == 1 and self.current_doc_title:
                markdown_lines.append(f"# {self.current_doc_title}\n")
            markdown_lines.append(f"## Página {page_num}\n")
        prev_was_heading = False
        for block in blocks:
            text = self.clean_text(block["text"])
            if not text:
                continue
            is_heading = self.is_heading(text, block["font_size"], avg_font_size)
            if is_heading:
                if page_num == 1 and not self.current_doc_title and not markdown_lines:
                    markdown_lines.append(f"# {text}\n")
                    self.current_doc_title = text
                else:
                    markdown_lines.append(f"\n### {text}\n")
                prev_was_heading = True
            else:
                if prev_was_heading:
                    markdown_lines.append(f"\n{text}\n")
                else:
                    markdown_lines.append(f"{text}\n")
                prev_was_heading = False
        return "".join(markdown_lines)

    def convert_pdf_to_markdown(self, pdf_path, output_path=None):
        try:
            doc = fitz.open(pdf_path)
            if output_path is None:
                output_path = str(Path(pdf_path).with_suffix('.md'))
            markdown_content = []
            total_pages = len(doc)
            print(f"  📄 {Path(pdf_path).name} ({total_pages} páginas)")
            for page_num in range(total_pages):
                page = doc[page_num]
                blocks = self.extract_text_with_formatting(page)
                page_markdown = self.format_as_markdown(blocks, page_num + 1, total_pages)
                markdown_content.append(page_markdown)
                if page_num < total_pages - 1 and total_pages > 1:
                    markdown_content.append("\n---\n\n")
                print(f"     ✓ Página {page_num + 1}/{total_pages}")
            final_markdown = "".join(markdown_content)
            final_markdown = re.sub(r'\n{3,}', '\n\n', final_markdown)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_markdown)
            doc.close()
            print(f"  ✅ Salvo: {Path(output_path).name}\n")
            return output_path
        except Exception as e:
            print(f"  ❌ Erro: {str(e)}\n")
            return None

pdf_dir = sys.argv[1]
pdf_files = list(Path(pdf_dir).glob('*.pdf'))
if not pdf_files:
    print("❌ Nenhum PDF encontrado")
    sys.exit(1)
print(f"\n📁 Encontrados {len(pdf_files)} arquivos PDF\n")
converter = PDFToMarkdownConverter()
converted = []
for pdf_file in sorted(pdf_files):
    result = converter.convert_pdf_to_markdown(str(pdf_file))
    if result:
        converted.append(result)
print("═" * 50)
print(f"\n🎉 Conversão concluída!")
print(f"✅ {len(converted)}/{len(pdf_files)} arquivo(s) convertido(s)\n")
if converted:
    print("Arquivos gerados:")
    for f in converted:
        print(f"  • {f}")
PYTHON_EOF
)

# Conta quantos PDFs existem
PDF_COUNT=$(find "$PDF_DIR" -maxdepth 1 -name "*.pdf" | wc -l | tr -d ' ')

if [ "$PDF_COUNT" -eq 0 ]; then
    echo -e "${RED}❌ Nenhum arquivo PDF encontrado em: $PDF_DIR${NC}"
    exit 1
fi

echo -e "\n${BLUE}📂 Pasta: $PDF_DIR${NC}"
echo -e "${BLUE}📊 Arquivos PDF encontrados: $PDF_COUNT${NC}\n"

# Executa o script Python
echo "$PYTHON_SCRIPT" | python3 - "$PDF_DIR"

echo -e "\n${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}        ✨ Conversão concluída com sucesso! ✨${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}\n"
