# 📄 Como Converter seus PDFs Escaneados para Markdown

## ⚡ SOLUÇÃO RÁPIDA (2 minutos)

Seus PDFs são **documentos escaneados** que precisam de **OCR** primeiro!

### 🚀 Opção 1: Script Bash Simplificado (RECOMENDADO)

Copie e cole no Terminal:

```bash
# 1. Instalar dependências
brew install tesseract tesseract-lang poppler

# 2. Baixar o script
curl -o ~/Desktop/converter_ocr.sh https://raw.githubusercontent.com/geekia-pt/ocr/claude/pdf-to-markdown-sehxh/convert_with_tesseract.sh

# 3. Executar
chmod +x ~/Desktop/converter_ocr.sh
~/Desktop/converter_ocr.sh "/Users/macbook_pro/Desktop/PDF TO MD"
```

**Pronto!** Os arquivos `.md` serão criados com o texto extraído via OCR.

---

### 🐍 Opção 2: Script Python (Mais Avançado)

```bash
# 1. Instalar dependências
brew install tesseract tesseract-lang poppler
pip3 install pytesseract pdf2image Pillow

# 2. Baixar o script
curl -o ~/Desktop/ocr_converter.py https://raw.githubusercontent.com/geekia-pt/ocr/claude/pdf-to-markdown-sehxh/ocr_pdf_to_markdown.py

# 3. Executar
python3 ~/Desktop/ocr_converter.py "/Users/macbook_pro/Desktop/PDF TO MD"
```

---

## 📊 O Que Vai Acontecer

```
═══════════════════════════════════════════════════════════
   OCR PDF to Markdown - Usando Tesseract OCR
═══════════════════════════════════════════════════════════

✅ Tesseract: tesseract 5.3.0
✅ Conversor: pdftoppm
✅ Idioma português disponível

📂 Pasta: /Users/macbook_pro/Desktop/PDF TO MD

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 [1] Processando: documento1.pdf
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   📊 Total de páginas: 5
   🔄 Convertendo PDF para imagens...

   ✅ 5 imagem(ns) gerada(s)
   🔍 Iniciando OCR (idioma: por)...

   📖 Página 1/5:
      🔍 Fazendo OCR...
      ✅ Extraído: 1847 caracteres
      💬 Preview: TÍTULO DO DOCUMENTO Este é o texto extraído...

   📖 Página 2/5:
      🔍 Fazendo OCR...
      ✅ Extraído: 2104 caracteres
      💬 Preview: Continuação do texto na segunda página...

   [... mais páginas ...]

✅ Conversão concluída!
📁 Salvo em: documento1.md
📊 Tamanho: 9425 bytes

[Processa os outros 2 PDFs...]

═══════════════════════════════════════════════════════════
🎉 Conversão finalizada!
✅ 3/3 arquivo(s) convertido(s) com sucesso
═══════════════════════════════════════════════════════════

Arquivos gerados:
  • documento1.md (9425 bytes)
  • documento2.md (7831 bytes)
  • documento3.md (12543 bytes)
```

---

## 📁 Resultado Final

```
/Users/macbook_pro/Desktop/PDF TO MD/
├── documento1.pdf
├── documento1.md  ← COM TEXTO EXTRAÍDO!
├── documento2.pdf
├── documento2.md  ← COM TEXTO EXTRAÍDO!
├── documento3.pdf
└── documento3.md  ← COM TEXTO EXTRAÍDO!
```

---

## ❓ Qual Script Usar?

| Característica | Script Bash | Script Python |
|---------------|-------------|---------------|
| **Facilidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Dependências** | Menos | Mais |
| **Velocidade** | Rápido | Médio |
| **Formatação** | Básica | Avançada |
| **Limpeza de Texto** | Simples | Inteligente |
| **Detecção de Títulos** | Básica | Avançada |

**Recomendação**: Use o **Script Bash** para simplicidade, ou o **Script Python** se quiser melhor formatação.

---

## 🔧 Solução de Problemas

### "command not found: brew"

```bash
# Instalar Homebrew primeiro
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### "Tesseract not found"

```bash
brew install tesseract tesseract-lang
```

### "Unable to load PDF"

```bash
brew install poppler
```

### Texto extraído com erros

- **Aumente a qualidade**: PDFs com resolução mínima de 300 DPI
- **Verifique o idioma**: Certifique-se que instalou `tesseract-lang`
- **Re-escaneie**: Se possível, escaneie novamente com maior qualidade

### Processo muito lento

- **Normal**: OCR é intensivo, pode levar 5-10 segundos por página
- **Múltiplos PDFs**: Processe um por vez se estiver lento
- **Reduzir DPI**: No script, mude `300` para `150` (menos qualidade, mais rápido)

---

## ⏱️ Quanto Tempo Demora?

**Por página (300 DPI)**:
- Texto simples: ~5-8 segundos
- Texto denso: ~10-15 segundos
- Imagens complexas: ~15-20 segundos

**Seus 3 PDFs**:
- Se cada um tiver ~10 páginas: **5-10 minutos total**
- Se cada um tiver ~50 páginas: **20-40 minutos total**

---

## 🎯 Diferença dos Scripts Anteriores

| Script | Funciona com | Resultado |
|--------|--------------|-----------|
| `pdf_to_markdown_converter.py` | PDFs com texto selecionável | ❌ Vazio (seus PDFs são escaneados) |
| `ocr_pdf_to_markdown.py` | PDFs escaneados (imagens) | ✅ Extrai texto via OCR |
| `convert_with_tesseract.sh` | PDFs escaneados (imagens) | ✅ Extrai texto via OCR |

**Seus PDFs precisam de OCR!** Use os dois últimos scripts.

---

## 📚 Documentação Completa

- **INSTRUCOES_OCR.md**: Guia detalhado com todas as opções
- **COMO_CONVERTER.md**: Instruções gerais
- **MARKDOWN_RENDERER.md**: Documentação técnica do renderer

---

## 🆘 Ainda com Problemas?

### Opção Fácil: Conversor Online

Use um destes (com OCR incluído):

1. **OnlineOCR**: https://www.onlineocr.net/
   - Gratuito, 15 arquivos/hora
   - Suporta português
   - Converte direto para TXT/DOCX

2. **PDF2GO**: https://www.pdf2go.com/ocr-pdf
   - Gratuito, 3 arquivos/dia
   - OCR em português
   - Boa qualidade

3. **Adobe Acrobat Online**: https://www.adobe.com/acrobat/online/ocr-pdf.html
   - Alta qualidade
   - Requer conta Adobe (gratuita)

**Depois de converter online para TXT**, você pode formatar manualmente como Markdown.

---

## ✅ Checklist Rápido

Para converter seus 3 PDFs:

- [ ] Instalei Homebrew (se necessário)
- [ ] Executei: `brew install tesseract tesseract-lang poppler`
- [ ] Baixei um dos scripts (Bash ou Python)
- [ ] Executei o script apontando para a pasta dos PDFs
- [ ] Tenho os 3 arquivos .md com texto extraído! 🎉

---

## 💬 Precisa de Ajuda?

Se algo não funcionar:

1. **Copie a mensagem de erro completa**
2. **Me envie aqui no chat**
3. Vou ajustar o script ou criar uma solução alternativa

**Estou aqui para garantir que você consiga converter seus PDFs!** 🔍📄➡️📝
