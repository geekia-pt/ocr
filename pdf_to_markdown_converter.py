#!/usr/bin/env python3
"""
PDF to Markdown Converter
Converte arquivos PDF para Markdown usando PyMuPDF (fitz) e formatação inteligente.

Uso:
    python3 pdf_to_markdown_converter.py "/caminho/para/pasta/com/pdfs"

Ou para converter um único arquivo:
    python3 pdf_to_markdown_converter.py "/caminho/para/arquivo.pdf"
"""

import os
import sys
import re
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("❌ Erro: PyMuPDF não está instalado.")
    print("Por favor, instale com: pip3 install PyMuPDF")
    sys.exit(1)


class PDFToMarkdownConverter:
    """Conversor de PDF para Markdown com formatação inteligente."""

    def __init__(self):
        self.current_doc_title = ""

    def is_heading(self, text, font_size, avg_font_size):
        """Detecta se uma linha é um cabeçalho baseado em tamanho de fonte e conteúdo."""
        if not text or len(text.strip()) == 0:
            return False

        text = text.strip()

        # Cabeçalho se a fonte for significativamente maior
        if font_size > avg_font_size * 1.2:
            return True

        # Cabeçalho se for curto e em maiúsculas/título
        if len(text) < 60:
            upper_count = sum(1 for c in text if c.isupper())
            alpha_count = sum(1 for c in text if c.isalpha())

            if alpha_count > 0 and upper_count / alpha_count > 0.7:
                return True

        return False

    def clean_text(self, text):
        """Limpa e normaliza o texto."""
        # Remove espaços múltiplos
        text = re.sub(r' +', ' ', text)
        # Remove quebras de linha no meio de palavras
        text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
        # Normaliza quebras de linha
        text = re.sub(r'\n+', '\n', text)
        return text.strip()

    def extract_text_with_formatting(self, page):
        """Extrai texto de uma página com informações de formatação."""
        blocks = []

        # Extrai blocos de texto com formatação
        text_dict = page.get_text("dict")

        for block in text_dict["blocks"]:
            if block["type"] == 0:  # Text block
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
        """Formata blocos de texto como Markdown."""
        if not blocks:
            return ""

        # Calcula tamanho médio de fonte
        avg_font_size = sum(b["font_size"] for b in blocks) / len(blocks)

        markdown_lines = []

        # Adiciona cabeçalho de página se houver múltiplas páginas
        if total_pages > 1:
            if page_num == 1 and self.current_doc_title:
                markdown_lines.append(f"# {self.current_doc_title}\n")
            markdown_lines.append(f"## Página {page_num}\n")

        prev_was_heading = False
        prev_was_empty = False

        for block in blocks:
            text = self.clean_text(block["text"])

            if not text:
                continue

            is_heading = self.is_heading(text, block["font_size"], avg_font_size)

            if is_heading:
                # Primeiro título pode ser o título do documento
                if page_num == 1 and not self.current_doc_title and not markdown_lines:
                    markdown_lines.append(f"# {text}\n")
                    self.current_doc_title = text
                else:
                    markdown_lines.append(f"\n### {text}\n")
                prev_was_heading = True
                prev_was_empty = False
            else:
                # Texto normal
                if prev_was_heading or prev_was_empty:
                    markdown_lines.append(f"\n{text}\n")
                else:
                    markdown_lines.append(f"{text}\n")
                prev_was_heading = False
                prev_was_empty = False

        return "".join(markdown_lines)

    def convert_pdf_to_markdown(self, pdf_path, output_path=None):
        """Converte um arquivo PDF para Markdown."""
        try:
            # Abre o PDF
            doc = fitz.open(pdf_path)

            # Define o caminho de saída
            if output_path is None:
                output_path = str(Path(pdf_path).with_suffix('.md'))

            markdown_content = []
            total_pages = len(doc)

            print(f"📄 Processando: {Path(pdf_path).name} ({total_pages} páginas)")

            # Processa cada página
            for page_num in range(total_pages):
                page = doc[page_num]
                blocks = self.extract_text_with_formatting(page)

                page_markdown = self.format_as_markdown(blocks, page_num + 1, total_pages)
                markdown_content.append(page_markdown)

                # Adiciona separador entre páginas
                if page_num < total_pages - 1 and total_pages > 1:
                    markdown_content.append("\n---\n\n")

                print(f"  ✓ Página {page_num + 1}/{total_pages}")

            # Junta todo o conteúdo
            final_markdown = "".join(markdown_content)

            # Remove linhas vazias excessivas
            final_markdown = re.sub(r'\n{3,}', '\n\n', final_markdown)

            # Salva o arquivo
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_markdown)

            doc.close()

            print(f"✅ Convertido com sucesso: {output_path}\n")
            return output_path

        except Exception as e:
            print(f"❌ Erro ao converter {pdf_path}: {str(e)}\n")
            return None


def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("Uso: python3 pdf_to_markdown_converter.py <caminho_para_pdf_ou_pasta>")
        print("\nExemplos:")
        print('  python3 pdf_to_markdown_converter.py "/Users/macbook_pro/Desktop/PDF TO MD"')
        print('  python3 pdf_to_markdown_converter.py "documento.pdf"')
        sys.exit(1)

    path = sys.argv[1]

    if not os.path.exists(path):
        print(f"❌ Erro: O caminho '{path}' não existe.")
        sys.exit(1)

    converter = PDFToMarkdownConverter()
    converted_files = []

    # Se for um arquivo PDF
    if os.path.isfile(path) and path.lower().endswith('.pdf'):
        result = converter.convert_pdf_to_markdown(path)
        if result:
            converted_files.append(result)

    # Se for uma pasta
    elif os.path.isdir(path):
        pdf_files = list(Path(path).glob('*.pdf'))

        if not pdf_files:
            print(f"❌ Nenhum arquivo PDF encontrado em: {path}")
            sys.exit(1)

        print(f"📁 Encontrados {len(pdf_files)} arquivos PDF\n")
        print("=" * 60)

        for pdf_file in pdf_files:
            result = converter.convert_pdf_to_markdown(str(pdf_file))
            if result:
                converted_files.append(result)

    else:
        print(f"❌ Erro: '{path}' não é um arquivo PDF ou pasta válida.")
        sys.exit(1)

    # Resumo
    print("=" * 60)
    print(f"\n🎉 Conversão concluída!")
    print(f"✅ {len(converted_files)} arquivo(s) convertido(s) com sucesso\n")

    if converted_files:
        print("Arquivos gerados:")
        for f in converted_files:
            print(f"  • {f}")


if __name__ == "__main__":
    main()
