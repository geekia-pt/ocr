# Tesseract Markdown Renderer

Este documento descreve como usar o novo renderer Markdown do Tesseract OCR para converter PDFs em arquivos Markdown.

## Funcionalidade

O **TessMarkdownRenderer** é um novo renderer adicionado ao Tesseract OCR que permite converter documentos (incluindo PDFs) em arquivos Markdown formatados.

### Características

- ✅ Conversão de PDF para Markdown (.md)
- ✅ Formatação automática de cabeçalhos
- ✅ Separação de páginas com divisores horizontais
- ✅ Detecção inteligente de parágrafos
- ✅ Preservação da estrutura do documento
- ✅ Suporte a múltiplas páginas

## Arquivos Modificados/Criados

1. **src/api/markdownrenderer.cpp** - Implementação do renderer Markdown
2. **src/api/renderer.h** - Declaração da classe TessMarkdownRenderer
3. **src/api/tesseractmain.cpp** - Registro do renderer no CLI
4. **CMakeLists.txt** - Adição ao sistema de build
5. **tessdata/configs/md** - Arquivo de configuração para saída Markdown

## Como Usar

### Opção 1: Usando o arquivo de configuração

```bash
tesseract input.pdf output md
```

Isso criará um arquivo `output.md` com o conteúdo do PDF convertido para Markdown.

### Opção 2: Usando variável de configuração

```bash
tesseract input.pdf output -c tessedit_create_md=1
```

### Opção 3: Múltiplos formatos simultaneamente

Você pode gerar Markdown junto com outros formatos:

```bash
tesseract input.pdf output txt md pdf
```

Isso criará:
- `output.txt` - Texto simples
- `output.md` - Markdown formatado
- `output.pdf` - PDF pesquisável

## Exemplo de Saída

Para um PDF com título e múltiplas páginas, a saída será algo como:

```markdown
# Nome do Documento

## Page 1

Conteúdo da primeira página aqui...

---

## Page 2

Conteúdo da segunda página aqui...
```

## Formatação Automática

O renderer inclui formatação inteligente que:

1. **Detecta cabeçalhos**: Linhas curtas em maiúsculas ou title case são convertidas em cabeçalhos (`###`)
2. **Separa páginas**: Cada página é marcada com `---` (divisor horizontal) e um cabeçalho de página
3. **Organiza parágrafos**: Linhas vazias são usadas para separar parágrafos
4. **Preserva título**: O título do documento (se fornecido) aparece como cabeçalho principal (`#`)

## Compilação

Para compilar o Tesseract com o novo renderer:

```bash
mkdir build
cd build
cmake ..
make
sudo make install
```

## Requisitos

- Tesseract OCR 4.0+
- Leptonica 1.74+
- CMake 3.5+
- Compilador C++11 ou superior

## Uso Programático (API C++)

```cpp
#include "baseapi.h"
#include "renderer.h"

tesseract::TessBaseAPI api;
api.Init(nullptr, "eng", tesseract::OEM_DEFAULT);

tesseract::TessMarkdownRenderer renderer("output");
api.ProcessPages("input.pdf", nullptr, 0, &renderer);
```

## Notas

- O renderer funciona com qualquer formato de imagem suportado pelo Tesseract (PNG, JPG, TIFF, PDF, etc.)
- A qualidade da conversão depende da qualidade do OCR e da clareza do documento original
- Para melhores resultados, use documentos com resolução de pelo menos 300 DPI

## Autor

Implementado por Claude AI Assistant para conversão de PDF para Markdown.

## Licença

Apache License 2.0 (mesma licença do Tesseract OCR)
