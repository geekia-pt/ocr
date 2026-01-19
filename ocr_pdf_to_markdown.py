#!/usr/bin/env python3
"""
OCR PDF to Markdown Converter
Faz OCR em PDFs escaneados e converte para Markdown formatado.

Requer: pytesseract, pdf2image, Pillow
Uso: python3 ocr_pdf_to_markdown.py "/caminho/para/pasta/com/pdfs"
"""

import os
import sys
import re
from pathlib import Path

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError as e:
    print("❌ Erro: Dependências não instaladas.")
    print("\nInstale com os seguintes comandos:")
    print("  pip3 install pytesseract pdf2image Pillow")
    print("\nNo macOS, também instale:")
    print("  brew install tesseract")
    print("  brew install poppler")
    sys.exit(1)


class OCRPDFToMarkdown:
    """Conversor de PDF escaneado para Markdown usando OCR."""

    def __init__(self, language='por'):
        """
        Inicializa o conversor.

        Args:
            language: Idioma para OCR (por=Português, eng=Inglês, por+eng=ambos)
        """
        self.language = language
        self.current_doc_title = ""

    def is_heading(self, text):
        """Detecta se uma linha é um cabeçalho."""
        if not text or len(text.strip()) == 0:
            return False

        text = text.strip()

        # Cabeçalho se for curto e em maiúsculas/título
        if len(text) < 60 and len(text) > 3:
            upper_count = sum(1 for c in text if c.isupper())
            alpha_count = sum(1 for c in text if c.isalpha())

            if alpha_count > 0 and upper_count / alpha_count > 0.7:
                return True

            # Verifica se começa com maiúscula e parece título
            if text[0].isupper() and not text.endswith('.'):
                words = text.split()
                if len(words) <= 8 and sum(1 for w in words if w[0].isupper()) / len(words) > 0.5:
                    return True

        return False

    def clean_text(self, text):
        """Limpa e normaliza o texto extraído por OCR."""
        # Remove linhas vazias múltiplas
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        # Remove espaços múltiplos
        text = re.sub(r' +', ' ', text)

        # Remove quebras de linha no meio de palavras (hifenização)
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)

        # Junta linhas que não terminam com pontuação
        lines = text.split('\n')
        cleaned_lines = []
        temp_line = ""

        for line in lines:
            line = line.strip()
            if not line:
                if temp_line:
                    cleaned_lines.append(temp_line)
                    temp_line = ""
                cleaned_lines.append("")
                continue

            if temp_line and not temp_line[-1] in '.!?:;':
                temp_line += " " + line
            else:
                if temp_line:
                    cleaned_lines.append(temp_line)
                temp_line = line

        if temp_line:
            cleaned_lines.append(temp_line)

        return '\n'.join(cleaned_lines).strip()

    def format_as_markdown(self, text, page_num, total_pages):
        """Formata texto como Markdown."""
        if not text or not text.strip():
            return ""

        lines = text.split('\n')
        markdown_lines = []

        # Adiciona cabeçalho de página se houver múltiplas páginas
        if total_pages > 1:
            if page_num == 1 and self.current_doc_title:
                markdown_lines.append(f"# {self.current_doc_title}\n")
            markdown_lines.append(f"## Página {page_num}\n")

        prev_was_heading = False
        prev_was_empty = False

        for line in lines:
            line = line.strip()

            # Linha vazia
            if not line:
                if not prev_was_empty:
                    markdown_lines.append("")
                prev_was_empty = True
                continue

            prev_was_empty = False

            # Detecta cabeçalho
            if self.is_heading(line):
                # Primeiro cabeçalho pode ser título do documento
                if page_num == 1 and not self.current_doc_title and len(markdown_lines) <= 1:
                    markdown_lines.append(f"# {line}\n")
                    self.current_doc_title = line
                else:
                    markdown_lines.append(f"\n### {line}\n")
                prev_was_heading = True
            else:
                # Texto normal
                markdown_lines.append(line)
                prev_was_heading = False

        result = '\n'.join(markdown_lines)

        # Remove linhas vazias excessivas
        result = re.sub(r'\n{3,}', '\n\n', result)

        return result + "\n"

    def ocr_image(self, image):
        """Faz OCR em uma imagem e retorna o texto."""
        try:
            # Configurações para melhor qualidade de OCR
            custom_config = r'--oem 3 --psm 6'

            # Faz OCR
            text = pytesseract.image_to_string(
                image,
                lang=self.language,
                config=custom_config
            )

            return text
        except Exception as e:
            print(f"      ⚠️ Erro no OCR: {str(e)}")
            return ""

    def convert_pdf_to_markdown(self, pdf_path, output_path=None, dpi=300):
        """
        Converte um PDF escaneado para Markdown usando OCR.

        Args:
            pdf_path: Caminho do arquivo PDF
            output_path: Caminho de saída (opcional)
            dpi: Resolução para conversão (300 recomendado)
        """
        try:
            # Define o caminho de saída
            if output_path is None:
                output_path = str(Path(pdf_path).with_suffix('.md'))

            print(f"\n📄 Processando: {Path(pdf_path).name}")
            print(f"   🔄 Convertendo PDF para imagens (DPI: {dpi})...")

            # Converte PDF para imagens
            try:
                images = convert_from_path(pdf_path, dpi=dpi)
            except Exception as e:
                print(f"   ❌ Erro ao converter PDF: {str(e)}")
                print(f"   💡 Certifique-se de que poppler está instalado: brew install poppler")
                return None

            total_pages = len(images)
            print(f"   📊 Total de páginas: {total_pages}")
            print(f"   🔍 Iniciando OCR (idioma: {self.language})...\n")

            markdown_content = []

            # Processa cada página
            for page_num, image in enumerate(images, start=1):
                print(f"   📖 Página {page_num}/{total_pages}:")
                print(f"      🔍 Fazendo OCR...")

                # Faz OCR na imagem
                text = self.ocr_image(image)

                if not text.strip():
                    print(f"      ⚠️ Nenhum texto detectado")
                    continue

                # Limpa o texto
                cleaned_text = self.clean_text(text)

                # Formata como Markdown
                page_markdown = self.format_as_markdown(cleaned_text, page_num, total_pages)
                markdown_content.append(page_markdown)

                # Adiciona separador entre páginas
                if page_num < total_pages:
                    markdown_content.append("\n---\n\n")

                # Mostra preview do texto extraído
                preview = cleaned_text[:100].replace('\n', ' ')
                if len(cleaned_text) > 100:
                    preview += "..."
                print(f"      ✅ Extraído: {len(cleaned_text)} caracteres")
                print(f"      💬 Preview: {preview}\n")

            # Junta todo o conteúdo
            final_markdown = "".join(markdown_content)

            # Remove linhas vazias excessivas
            final_markdown = re.sub(r'\n{4,}', '\n\n\n', final_markdown)

            # Salva o arquivo
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_markdown)

            print(f"✅ Convertido com sucesso!")
            print(f"📁 Salvo em: {output_path}")
            print(f"📊 Total de caracteres: {len(final_markdown)}\n")

            return output_path

        except Exception as e:
            print(f"❌ Erro ao processar {pdf_path}: {str(e)}\n")
            import traceback
            traceback.print_exc()
            return None


def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    errors = []

    # Verifica Tesseract
    try:
        pytesseract.get_tesseract_version()
    except Exception:
        errors.append("❌ Tesseract OCR não encontrado. Instale com: brew install tesseract")

    # Verifica poppler (necessário para pdf2image)
    try:
        from pdf2image import convert_from_path
        # Tenta converter uma página fictícia para verificar poppler
    except Exception:
        pass  # pdf2image está instalado, poppler será testado na conversão

    return errors


def main():
    """Função principal."""
    print("=" * 70)
    print("  📄 OCR PDF to Markdown Converter")
    print("  🔍 Converte PDFs escaneados para Markdown usando OCR")
    print("=" * 70)

    if len(sys.argv) < 2:
        print("\n❌ Uso incorreto!")
        print("\nUso: python3 ocr_pdf_to_markdown.py <caminho_para_pdf_ou_pasta>")
        print("\nExemplos:")
        print('  python3 ocr_pdf_to_markdown.py "/Users/macbook_pro/Desktop/PDF TO MD"')
        print('  python3 ocr_pdf_to_markdown.py "documento.pdf"')
        print("\nOpções de idioma:")
        print("  Edite a linha 'language=' no código para:")
        print("    - 'por' (Português)")
        print("    - 'eng' (Inglês)")
        print("    - 'por+eng' (Português + Inglês)")
        sys.exit(1)

    path = sys.argv[1]

    if not os.path.exists(path):
        print(f"\n❌ Erro: O caminho '{path}' não existe.")
        sys.exit(1)

    # Verifica dependências
    print("\n🔍 Verificando dependências...")
    errors = check_dependencies()
    if errors:
        for error in errors:
            print(error)
        sys.exit(1)
    print("✅ Todas as dependências instaladas\n")

    # Detecta idioma (pode ser configurado)
    language = 'por'  # Português por padrão

    # Verifica se há idioma português instalado
    try:
        available_langs = pytesseract.get_languages()
        if 'por' not in available_langs and 'eng' in available_langs:
            print("⚠️ Idioma português não encontrado, usando inglês")
            print("💡 Para instalar português: brew install tesseract-lang")
            language = 'eng'
    except:
        pass

    converter = OCRPDFToMarkdown(language=language)
    converted_files = []

    # Se for um arquivo PDF
    if os.path.isfile(path) and path.lower().endswith('.pdf'):
        result = converter.convert_pdf_to_markdown(path)
        if result:
            converted_files.append(result)

    # Se for uma pasta
    elif os.path.isdir(path):
        pdf_files = sorted(Path(path).glob('*.pdf'))

        if not pdf_files:
            print(f"❌ Nenhum arquivo PDF encontrado em: {path}")
            sys.exit(1)

        print(f"📁 Encontrados {len(pdf_files)} arquivos PDF")
        print("=" * 70)

        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] Processando arquivo...")
            result = converter.convert_pdf_to_markdown(str(pdf_file))
            if result:
                converted_files.append(result)

    else:
        print(f"❌ Erro: '{path}' não é um arquivo PDF ou pasta válida.")
        sys.exit(1)

    # Resumo
    print("=" * 70)
    print(f"\n🎉 Conversão concluída!")
    print(f"✅ {len(converted_files)}/{len(pdf_files) if 'pdf_files' in locals() else 1} arquivo(s) convertido(s)\n")

    if converted_files:
        print("Arquivos gerados:")
        for f in converted_files:
            size = os.path.getsize(f)
            print(f"  • {f} ({size:,} bytes)")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
