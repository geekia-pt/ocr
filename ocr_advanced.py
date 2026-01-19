#!/usr/bin/env python3
"""
OCR PDF to Markdown - Versão com Qualidade Melhorada
Usa pré-processamento de imagem e configurações avançadas do Tesseract

Autor: Claude AI
Data: 2026-01-19
"""

import os
import sys
import re
from pathlib import Path

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image, ImageEnhance, ImageFilter
    import numpy as np
except ImportError as e:
    print("❌ Erro: Dependências não instaladas.")
    print("\nInstale com:")
    print("  pip3 install pytesseract pdf2image Pillow numpy")
    print("\nNo macOS:")
    print("  brew install tesseract tesseract-lang poppler")
    sys.exit(1)


class AdvancedOCRConverter:
    """Conversor de PDF para Markdown com OCR de alta qualidade."""

    def __init__(self, language='por+eng', dpi=600):
        """
        Inicializa o conversor.

        Args:
            language: Idioma para OCR (por+eng recomendado)
            dpi: Resolução (600 recomendado para qualidade)
        """
        self.language = language
        self.dpi = dpi
        self.current_doc_title = ""

    def preprocess_image(self, image):
        """
        Pré-processa a imagem para melhorar qualidade do OCR.

        Aplicações:
        1. Converte para escala de cinza
        2. Aumenta contraste
        3. Aumenta nitidez
        4. Aplica binarização (threshold)
        """
        # Converte para RGB se necessário
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Converte para escala de cinza
        gray = image.convert('L')

        # Aumenta contraste
        enhancer = ImageEnhance.Contrast(gray)
        contrast = enhancer.enhance(2.0)

        # Aumenta nitidez
        sharpener = ImageEnhance.Sharpness(contrast)
        sharp = sharpener.enhance(2.0)

        # Binarização adaptativa (melhora muito texto escaneado)
        # Converte para numpy array
        img_array = np.array(sharp)

        # Threshold otimizado para documentos
        threshold = 128
        binary = np.where(img_array > threshold, 255, 0).astype(np.uint8)

        # Converte de volta para PIL Image
        processed = Image.fromarray(binary)

        # Remove ruído com filtro de mediana
        processed = processed.filter(ImageFilter.MedianFilter(size=3))

        return processed

    def ocr_image_advanced(self, image, page_num):
        """
        Faz OCR com múltiplas tentativas e diferentes configurações.

        Testa diferentes PSM (Page Segmentation Modes):
        - PSM 1: Automatic page segmentation with OSD
        - PSM 3: Fully automatic page segmentation (padrão)
        - PSM 4: Assume a single column of text
        - PSM 6: Assume a single uniform block of text
        """
        print(f"      📸 Pré-processando imagem...")

        # Pré-processa a imagem
        processed_image = self.preprocess_image(image)

        # Configurações otimizadas para documentos técnicos
        configs = [
            '--oem 1 --psm 3',  # Auto page segmentation (default)
            '--oem 1 --psm 4',  # Single column
            '--oem 1 --psm 6',  # Single uniform block
            '--oem 1 --psm 1',  # Auto with OSD
        ]

        best_text = ""
        best_confidence = 0

        print(f"      🔍 Testando diferentes modos de OCR...")

        for i, config in enumerate(configs, 1):
            try:
                # Faz OCR
                text = pytesseract.image_to_string(
                    processed_image,
                    lang=self.language,
                    config=config
                )

                # Tenta obter confiança (se disponível)
                try:
                    data = pytesseract.image_to_data(
                        processed_image,
                        lang=self.language,
                        config=config,
                        output_type=pytesseract.Output.DICT
                    )
                    confidences = [int(conf) for conf in data['conf'] if conf != '-1']
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                except:
                    avg_confidence = len(text)  # Usa tamanho como proxy

                print(f"         Modo {i}: {len(text)} chars, confiança: {avg_confidence:.1f}")

                # Mantém o melhor resultado
                if avg_confidence > best_confidence or len(text) > len(best_text):
                    best_text = text
                    best_confidence = avg_confidence

            except Exception as e:
                print(f"         Modo {i}: Erro - {str(e)}")
                continue

        return best_text

    def clean_text(self, text):
        """Limpa texto com algoritmo melhorado."""
        if not text:
            return ""

        # Remove caracteres de controle
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # Remove linhas com apenas símbolos/ruído
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()

            # Pula linhas muito curtas (provavelmente ruído)
            if len(line) < 3:
                continue

            # Pula linhas com mais de 50% de caracteres especiais
            special_chars = sum(1 for c in line if not c.isalnum() and c not in ' .,!?-:;()"\'')
            if len(line) > 0 and special_chars / len(line) > 0.5:
                continue

            # Pula linhas que parecem ser artefatos de OCR
            if re.match(r'^[\W_]{5,}$', line):
                continue

            cleaned_lines.append(line)

        # Junta linhas
        text = '\n'.join(cleaned_lines)

        # Remove espaços múltiplos
        text = re.sub(r' {2,}', ' ', text)

        # Remove quebras de linha múltiplas
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Junta palavras hifenizadas
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)

        # Junta linhas que não terminam com pontuação (parágrafos quebrados)
        lines = text.split('\n')
        result = []
        temp = ""

        for line in lines:
            line = line.strip()
            if not line:
                if temp:
                    result.append(temp)
                    temp = ""
                result.append("")
                continue

            # Se a linha anterior não termina com pontuação, junta
            if temp and not temp[-1] in '.!?:;':
                temp += " " + line
            else:
                if temp:
                    result.append(temp)
                temp = line

        if temp:
            result.append(temp)

        return '\n'.join(result).strip()

    def is_heading(self, text):
        """Detecta cabeçalhos com heurística melhorada."""
        if not text or len(text.strip()) < 3:
            return False

        text = text.strip()

        # Cabeçalho se for curto e maiúsculas
        if len(text) < 80:
            upper_count = sum(1 for c in text if c.isupper())
            alpha_count = sum(1 for c in text if c.isalpha())

            if alpha_count > 0:
                upper_ratio = upper_count / alpha_count

                # Muito em maiúsculas = cabeçalho
                if upper_ratio > 0.7:
                    return True

                # Começa com maiúscula e é curto
                if upper_ratio > 0.3 and len(text) < 50:
                    return True

        return False

    def format_as_markdown(self, text, page_num, total_pages):
        """Formata texto como Markdown."""
        if not text or not text.strip():
            return ""

        lines = text.split('\n')
        markdown_lines = []

        # Cabeçalho de página
        if total_pages > 1:
            if page_num == 1 and self.current_doc_title:
                markdown_lines.append(f"# {self.current_doc_title}\n")
            markdown_lines.append(f"## Página {page_num}\n")

        prev_was_heading = False

        for line in lines:
            line = line.strip()

            if not line:
                markdown_lines.append("")
                continue

            # Detecta cabeçalho
            if self.is_heading(line):
                if page_num == 1 and not self.current_doc_title and len(markdown_lines) <= 1:
                    markdown_lines.append(f"# {line}\n")
                    self.current_doc_title = line
                else:
                    markdown_lines.append(f"\n### {line}\n")
                prev_was_heading = True
            else:
                markdown_lines.append(line)
                prev_was_heading = False

        result = '\n'.join(markdown_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)

        return result + "\n"

    def convert_pdf_to_markdown(self, pdf_path, output_path=None):
        """Converte PDF para Markdown com qualidade melhorada."""
        try:
            if output_path is None:
                output_path = str(Path(pdf_path).with_suffix('.md'))

            print(f"\n{'='*70}")
            print(f"📄 Processando: {Path(pdf_path).name}")
            print(f"{'='*70}")
            print(f"⚙️  Configurações:")
            print(f"   • DPI: {self.dpi} (alta qualidade)")
            print(f"   • Idioma: {self.language}")
            print(f"   • Pré-processamento: ATIVADO")
            print(f"   • Múltiplas tentativas: ATIVADO\n")

            # Converte PDF para imagens com alta resolução
            print(f"🔄 Convertendo PDF para imagens ({self.dpi} DPI)...")
            print(f"   ⚠️  Isso pode demorar mais, mas a qualidade será melhor...\n")

            images = convert_from_path(pdf_path, dpi=self.dpi)
            total_pages = len(images)

            print(f"✅ {total_pages} página(s) convertida(s)\n")

            markdown_content = []
            total_chars = 0

            # Processa cada página
            for page_num, image in enumerate(images, start=1):
                print(f"📖 Página {page_num}/{total_pages}:")

                # Faz OCR com método avançado
                text = self.ocr_image_advanced(image, page_num)

                if not text.strip():
                    print(f"      ⚠️  Nenhum texto detectado\n")
                    continue

                # Limpa o texto
                print(f"      🧹 Limpando texto...")
                cleaned_text = self.clean_text(text)

                # Formata como Markdown
                page_markdown = self.format_as_markdown(cleaned_text, page_num, total_pages)
                markdown_content.append(page_markdown)

                # Separador entre páginas
                if page_num < total_pages:
                    markdown_content.append("\n---\n\n")

                # Estatísticas
                chars = len(cleaned_text)
                total_chars += chars
                words = len(cleaned_text.split())

                print(f"      ✅ Extraído: {chars} caracteres, {words} palavras")

                # Preview melhor
                preview_lines = [l for l in cleaned_text.split('\n') if len(l.strip()) > 10][:2]
                if preview_lines:
                    print(f"      💬 Preview:")
                    for pline in preview_lines:
                        print(f"         {pline[:70]}...")

                print()

            # Salva arquivo
            final_markdown = "".join(markdown_content)
            final_markdown = re.sub(r'\n{4,}', '\n\n\n', final_markdown)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_markdown)

            # Resumo
            print(f"{'='*70}")
            print(f"✅ Conversão concluída!")
            print(f"📁 Salvo em: {output_path}")
            print(f"📊 Estatísticas:")
            print(f"   • Total de caracteres: {total_chars:,}")
            print(f"   • Total de palavras: {len(final_markdown.split()):,}")
            print(f"   • Tamanho do arquivo: {len(final_markdown):,} bytes")
            print(f"   • Média por página: {total_chars // total_pages:,} caracteres")
            print(f"{'='*70}\n")

            return output_path

        except Exception as e:
            print(f"❌ Erro ao processar {pdf_path}: {str(e)}\n")
            import traceback
            traceback.print_exc()
            return None


def main():
    """Função principal."""
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║  📄 OCR PDF to Markdown - VERSÃO DE ALTA QUALIDADE".ljust(69) + "║")
    print("║  🔍 Pré-processamento + Múltiplas tentativas + Limpeza avançada".ljust(69) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝\n")

    if len(sys.argv) < 2:
        print("❌ Uso incorreto!\n")
        print("Uso: python3 ocr_advanced.py <pasta_com_pdfs>\n")
        print("Exemplo:")
        print('  python3 ocr_advanced.py "/Users/macbook_pro/Desktop/PDF TO MD"\n')
        sys.exit(1)

    path = sys.argv[1]

    if not os.path.exists(path):
        print(f"❌ Erro: O caminho '{path}' não existe.")
        sys.exit(1)

    # Configurações otimizadas
    print("⚙️  Configurações otimizadas:")
    print("   • DPI: 600 (qualidade máxima)")
    print("   • Idioma: Português + Inglês")
    print("   • Pré-processamento de imagem: ATIVADO")
    print("   • Múltiplos modos PSM: ATIVADO")
    print("   • Limpeza avançada de texto: ATIVADO\n")

    converter = AdvancedOCRConverter(language='por+eng', dpi=600)
    converted_files = []

    if os.path.isfile(path) and path.lower().endswith('.pdf'):
        result = converter.convert_pdf_to_markdown(path)
        if result:
            converted_files.append(result)
    elif os.path.isdir(path):
        pdf_files = sorted(Path(path).glob('*.pdf'))

        if not pdf_files:
            print(f"❌ Nenhum arquivo PDF encontrado em: {path}")
            sys.exit(1)

        print(f"📁 Encontrados {len(pdf_files)} arquivo(s) PDF\n")

        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n{'#'*70}")
            print(f"# [{i}/{len(pdf_files)}] Processando arquivo")
            print(f"{'#'*70}\n")

            result = converter.convert_pdf_to_markdown(str(pdf_file))
            if result:
                converted_files.append(result)
    else:
        print(f"❌ Erro: '{path}' não é um arquivo PDF ou pasta válida.")
        sys.exit(1)

    # Resumo final
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print(f"║  🎉 CONVERSÃO CONCLUÍDA!".ljust(69) + "║")
    print(f"║  ✅ {len(converted_files)}/{len(pdf_files) if 'pdf_files' in locals() else 1} arquivo(s) convertido(s) com sucesso".ljust(69) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝\n")

    if converted_files:
        print("Arquivos gerados:")
        for f in converted_files:
            size = os.path.getsize(f)
            print(f"  ✓ {Path(f).name}")
            print(f"    Tamanho: {size:,} bytes\n")


if __name__ == "__main__":
    main()
