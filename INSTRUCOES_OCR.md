# 🔍 Instruções para OCR de PDFs e Conversão para Markdown

## ⚡ O Problema

Seus PDFs são **documentos escaneados** (imagens), então precisam de **OCR (Reconhecimento Óptico de Caracteres)** para extrair o texto antes de converter para Markdown.

---

## 🚀 Solução Completa (macOS)

### Passo 1: Instalar Dependências

Copie e cole no Terminal do seu Mac:

```bash
# Instalar Homebrew (se ainda não tiver)
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Tesseract OCR com suporte a Português
brew install tesseract tesseract-lang

# Instalar Poppler (para converter PDF em imagens)
brew install poppler

# Instalar bibliotecas Python necessárias
pip3 install pytesseract pdf2image Pillow
```

### Passo 2: Baixar o Script OCR

```bash
cd ~/Desktop
curl -O https://raw.githubusercontent.com/geekia-pt/ocr/claude/pdf-to-markdown-sehxh/ocr_pdf_to_markdown.py
chmod +x ocr_pdf_to_markdown.py
```

### Passo 3: Converter os PDFs

```bash
python3 ~/Desktop/ocr_pdf_to_markdown.py "/Users/macbook_pro/Desktop/PDF TO MD"
```

---

## 📊 O que Você Verá

```
======================================================================
  📄 OCR PDF to Markdown Converter
  🔍 Converte PDFs escaneados para Markdown usando OCR
======================================================================

🔍 Verificando dependências...
✅ Todas as dependências instaladas

📁 Encontrados 3 arquivos PDF
======================================================================

[1/3] Processando arquivo...

📄 Processando: documento1.pdf
   🔄 Convertendo PDF para imagens (DPI: 300)...
   📊 Total de páginas: 5
   🔍 Iniciando OCR (idioma: por)...

   📖 Página 1/5:
      🔍 Fazendo OCR...
      ✅ Extraído: 1847 caracteres
      💬 Preview: TÍTULO DO DOCUMENTO Este é o conteúdo da primeira...

   📖 Página 2/5:
      🔍 Fazendo OCR...
      ✅ Extraído: 2134 caracteres
      💬 Preview: Continuação do texto na segunda página...

   [...]

✅ Convertido com sucesso!
📁 Salvo em: /Users/macbook_pro/Desktop/PDF TO MD/documento1.md
📊 Total de caracteres: 9425

[2/3] Processando arquivo...
[...]

======================================================================
🎉 Conversão concluída!
✅ 3/3 arquivo(s) convertido(s)

Arquivos gerados:
  • /Users/macbook_pro/Desktop/PDF TO MD/documento1.md (12,543 bytes)
  • /Users/macbook_pro/Desktop/PDF TO MD/documento2.md (8,921 bytes)
  • /Users/macbook_pro/Desktop/PDF TO MD/documento3.md (15,687 bytes)
======================================================================
```

---

## ⚙️ Configurações Avançadas

### Alterar Idioma do OCR

Edite o script e mude a linha:

```python
language = 'por'  # Português (padrão)
```

Para:

```python
language = 'eng'      # Inglês
language = 'por+eng'  # Português + Inglês (melhor para documentos mistos)
```

### Ajustar Qualidade/Velocidade

No script, localize:

```python
dpi=300  # Qualidade padrão
```

- **150 DPI**: Mais rápido, menor qualidade
- **300 DPI**: Balanceado (recomendado)
- **600 DPI**: Melhor qualidade, mais lento

---

## 🎯 Recursos do Script OCR

✅ **Reconhecimento OCR** de texto em imagens/PDFs escaneados
✅ **Suporte a Português** (e outros idiomas)
✅ **Detecção automática de cabeçalhos**
✅ **Limpeza inteligente** de texto (remove quebras de linha indevidas)
✅ **Formatação Markdown** automática
✅ **Separação de páginas** com divisores
✅ **Preview em tempo real** do texto extraído
✅ **Processamento em lote** de múltiplos PDFs

---

## 🔧 Solução de Problemas

### Erro: "Tesseract not found"

```bash
brew install tesseract
```

### Erro: "Unable to load PDF"

```bash
brew install poppler
```

### Erro: "No module named 'pytesseract'"

```bash
pip3 install pytesseract pdf2image Pillow
```

### Erro: "Language 'por' not found"

```bash
# Instalar pacote de idiomas
brew install tesseract-lang

# Ou verificar idiomas disponíveis
tesseract --list-langs
```

### OCR com Baixa Qualidade

1. **Aumente o DPI**: No script, mude `dpi=300` para `dpi=600`
2. **PDFs de baixa resolução**: Considere re-escanear com maior qualidade
3. **Texto muito pequeno**: Aumente o DPI para 600

---

## ⏱️ Tempo Estimado

Para PDFs escaneados:

- **1 página**: ~5-10 segundos
- **10 páginas**: ~1-2 minutos
- **50 páginas**: ~5-10 minutos

O tempo varia com:
- Resolução do PDF (DPI)
- Quantidade de texto por página
- Velocidade do processador

---

## 🎨 Exemplo de Saída Markdown

Para um PDF escaneado com 3 páginas:

```markdown
# TÍTULO DO DOCUMENTO

## Página 1

### Introdução

Este é o texto extraído da primeira página do documento.
O OCR reconheceu automaticamente o texto da imagem.

### Seção Principal

Continuação do conteúdo com parágrafos formatados
automaticamente.

---

## Página 2

### Segunda Seção

Texto da segunda página...

---

## Página 3

### Conclusão

Texto final do documento.
```

---

## 📝 Comandos Rápidos

### Converter um único PDF

```bash
python3 ocr_pdf_to_markdown.py "/Users/macbook_pro/Desktop/PDF TO MD/arquivo.pdf"
```

### Converter pasta inteira

```bash
python3 ocr_pdf_to_markdown.py "/Users/macbook_pro/Desktop/PDF TO MD"
```

### Verificar idiomas disponíveis

```bash
tesseract --list-langs
```

### Testar Tesseract manualmente

```bash
tesseract imagem.png saida -l por
cat saida.txt
```

---

## 🆘 Alternativas Online

Se não conseguir instalar as dependências, use conversores online com OCR:

1. **Online OCR**: https://www.onlineocr.net/
   - Suporta 46 idiomas
   - Converte para TXT/DOC/PDF
   - Limite: 15 arquivos/hora (grátis)

2. **PDF2GO**: https://www.pdf2go.com/ocr-pdf
   - OCR em português
   - Converte para vários formatos
   - Limite: 3 arquivos/dia (grátis)

3. **Adobe Online**: https://www.adobe.com/acrobat/online/ocr-pdf.html
   - Alta qualidade
   - Requer conta Adobe

---

## ✅ Checklist

- [ ] Instalei Homebrew
- [ ] Instalei Tesseract: `brew install tesseract tesseract-lang`
- [ ] Instalei Poppler: `brew install poppler`
- [ ] Instalei bibliotecas Python: `pip3 install pytesseract pdf2image Pillow`
- [ ] Baixei o script OCR
- [ ] Executei o comando de conversão
- [ ] Tenho os 3 arquivos .md com conteúdo extraído! 🎉

---

## 💡 Dica Pro

Para **melhor qualidade** de OCR:

1. **Use PDFs originais** quando possível (não re-escaneados)
2. **Resolução mínima**: 300 DPI
3. **Texto legível**: Fonte clara e sem distorções
4. **Contraste adequado**: Texto preto em fundo branco
5. **Rotação correta**: Documento na orientação certa

---

**Qualquer dúvida ou erro, me avise! Vou ajustar o script conforme necessário.** 🔍📄➡️📝
