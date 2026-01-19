# 🚀 Como Converter seus 3 PDFs para Markdown

## ⚡ Método Mais Rápido (1 comando apenas!)

### Passo 1: Copie este comando e execute no Terminal do seu Mac

```bash
curl -o ~/Desktop/converter.sh https://raw.githubusercontent.com/geekia-pt/ocr/claude/pdf-to-markdown-sehxh/converter_pdf_md.sh && chmod +x ~/Desktop/converter.sh && ~/Desktop/converter.sh "/Users/macbook_pro/Desktop/PDF TO MD"
```

**Isso vai:**
1. ✅ Baixar o script conversor
2. ✅ Torná-lo executável
3. ✅ Converter todos os 3 PDFs automaticamente
4. ✅ Criar os arquivos .md na mesma pasta

---

## 📋 Método Manual (se o automático não funcionar)

### Passo 1: Instalar PyMuPDF

```bash
pip3 install PyMuPDF
```

### Passo 2: Criar o script conversor

```bash
cat > ~/Desktop/converter.py << 'EOF'
import sys, os, re
from pathlib import Path
import fitz

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
                        blocks.append({"text": line_text, "font_size": avg_font_size, "bbox": line["bbox"]})
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
                markdown_lines.append(f"\n{text}\n" if prev_was_heading else f"{text}\n")
                prev_was_heading = False
        return "".join(markdown_lines)

    def convert_pdf_to_markdown(self, pdf_path, output_path=None):
        try:
            doc = fitz.open(pdf_path)
            if output_path is None:
                output_path = str(Path(pdf_path).with_suffix('.md'))
            markdown_content = []
            total_pages = len(doc)
            print(f"📄 {Path(pdf_path).name} ({total_pages} páginas)")
            for page_num in range(total_pages):
                page = doc[page_num]
                blocks = self.extract_text_with_formatting(page)
                page_markdown = self.format_as_markdown(blocks, page_num + 1, total_pages)
                markdown_content.append(page_markdown)
                if page_num < total_pages - 1 and total_pages > 1:
                    markdown_content.append("\n---\n\n")
                print(f"  ✓ Página {page_num + 1}/{total_pages}")
            final_markdown = re.sub(r'\n{3,}', '\n\n', "".join(markdown_content))
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_markdown)
            doc.close()
            print(f"✅ Salvo: {output_path}\n")
            return output_path
        except Exception as e:
            print(f"❌ Erro: {str(e)}\n")
            return None

pdf_dir = sys.argv[1] if len(sys.argv) > 1 else "."
pdf_files = list(Path(pdf_dir).glob('*.pdf'))
if not pdf_files:
    print("❌ Nenhum PDF encontrado")
    sys.exit(1)
print(f"\n📁 {len(pdf_files)} PDF(s) encontrado(s)\n")
converter = PDFToMarkdownConverter()
converted = [r for pdf in sorted(pdf_files) if (r := converter.convert_pdf_to_markdown(str(pdf)))]
print(f"\n🎉 {len(converted)}/{len(pdf_files)} convertido(s)!\n")
EOF
```

### Passo 3: Executar a conversão

```bash
python3 ~/Desktop/converter.py "/Users/macbook_pro/Desktop/PDF TO MD"
```

---

## 🎯 Resultado Esperado

Após executar o comando, você verá:

```
📁 3 PDF(s) encontrado(s)

📄 documento1.pdf (5 páginas)
  ✓ Página 1/5
  ✓ Página 2/5
  ✓ Página 3/5
  ✓ Página 4/5
  ✓ Página 5/5
✅ Salvo: /Users/macbook_pro/Desktop/PDF TO MD/documento1.md

📄 documento2.pdf (3 páginas)
  ✓ Página 1/3
  ✓ Página 2/3
  ✓ Página 3/3
✅ Salvo: /Users/macbook_pro/Desktop/PDF TO MD/documento2.md

📄 documento3.pdf (8 páginas)
  ✓ Página 1/8
  ...
✅ Salvo: /Users/macbook_pro/Desktop/PDF TO MD/documento3.md

🎉 3/3 convertido(s)!
```

---

## 📁 Os Arquivos .md Estarão em:

```
/Users/macbook_pro/Desktop/PDF TO MD/
├── documento1.pdf
├── documento1.md  ← NOVO!
├── documento2.pdf
├── documento2.md  ← NOVO!
├── documento3.pdf
└── documento3.md  ← NOVO!
```

---

## 🆘 Se Tiver Problemas

### Erro: "command not found: pip3"
```bash
# Instale o Python 3
brew install python3
```

### Erro: "ModuleNotFoundError: No module named 'fitz'"
```bash
# Instale PyMuPDF
pip3 install PyMuPDF
```

### Erro: "Permission denied"
```bash
# Torne o script executável
chmod +x ~/Desktop/converter.py
```

---

## 💡 Alternativa: Conversor Online

Se nada funcionar, use um destes conversores online:

1. **PDF2MD** - https://pdf2md.morethan.io/
2. **Aspose** - https://products.aspose.app/pdf/conversion/pdf-to-md
3. **CloudConvert** - https://cloudconvert.com/pdf-to-md

---

## ✅ Checklist

- [ ] Instalei PyMuPDF: `pip3 install PyMuPDF`
- [ ] Criei o script conversor
- [ ] Executei o comando de conversão
- [ ] Tenho os 3 arquivos .md criados! 🎉

---

**Qualquer problema, me avise! Estou aqui para ajudar!** 📄➡️📝
