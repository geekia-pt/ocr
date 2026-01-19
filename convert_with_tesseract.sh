#!/bin/bash
#
# Script de Conversão PDF para Markdown usando Tesseract OCR
# Usa o Tesseract diretamente (sem dependências Python)
#
# Requer: tesseract, imagemagick (ou poppler-utils)
# Uso: ./convert_with_tesseract.sh "/Users/macbook_pro/Desktop/PDF TO MD"
#

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   OCR PDF to Markdown - Usando Tesseract OCR${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

# Verifica argumentos
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

# Verifica Tesseract
if ! command -v tesseract &> /dev/null; then
    echo -e "${RED}❌ Tesseract não está instalado${NC}"
    echo -e "${YELLOW}Instale com: brew install tesseract tesseract-lang${NC}"
    exit 1
fi

# Verifica conversor de PDF para imagem
HAS_PDFTOPPM=false
HAS_CONVERT=false

if command -v pdftoppm &> /dev/null; then
    HAS_PDFTOPPM=true
    CONVERTER="pdftoppm"
elif command -v convert &> /dev/null; then
    HAS_CONVERT=true
    CONVERTER="imagemagick"
else
    echo -e "${RED}❌ Nenhum conversor de PDF encontrado${NC}"
    echo -e "${YELLOW}Instale um dos seguintes:${NC}"
    echo -e "${YELLOW}  brew install poppler      (para pdftoppm)${NC}"
    echo -e "${YELLOW}  brew install imagemagick  (para convert)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Tesseract: $(tesseract --version | head -1)${NC}"
echo -e "${GREEN}✅ Conversor: $CONVERTER${NC}\n"

# Verifica idioma
LANG="por"
if tesseract --list-langs 2>&1 | grep -q "por"; then
    echo -e "${GREEN}✅ Idioma português disponível${NC}"
else
    echo -e "${YELLOW}⚠️ Português não encontrado, usando inglês${NC}"
    echo -e "${YELLOW}💡 Instale com: brew install tesseract-lang${NC}"
    LANG="eng"
fi

echo -e "\n${BLUE}📂 Pasta: $PDF_DIR${NC}\n"

# Cria diretório temporário
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Contador
TOTAL_FILES=0
SUCCESS_FILES=0

# Processa cada PDF
for pdf_file in "$PDF_DIR"/*.pdf; do
    [ -e "$pdf_file" ] || continue

    TOTAL_FILES=$((TOTAL_FILES + 1))
    filename=$(basename "$pdf_file")
    basename="${filename%.pdf}"
    output_md="$PDF_DIR/$basename.md"

    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📄 [$TOTAL_FILES] Processando: $filename${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

    # Inicia arquivo Markdown
    > "$output_md"

    # Detecta número de páginas
    if command -v pdfinfo &> /dev/null; then
        NUM_PAGES=$(pdfinfo "$pdf_file" 2>/dev/null | grep "Pages:" | awk '{print $2}')
    else
        NUM_PAGES="?"
    fi

    echo -e "   📊 Total de páginas: ${NUM_PAGES}"
    echo -e "   🔄 Convertendo PDF para imagens...\n"

    # Converte PDF para imagens
    if [ "$HAS_PDFTOPPM" = true ]; then
        pdftoppm -png -r 300 "$pdf_file" "$TEMP_DIR/page"
    else
        convert -density 300 "$pdf_file" "$TEMP_DIR/page-%03d.png"
    fi

    # Conta páginas geradas
    page_count=$(ls "$TEMP_DIR"/page*.png 2>/dev/null | wc -l | tr -d ' ')

    if [ "$page_count" -eq 0 ]; then
        echo -e "${RED}   ❌ Erro ao converter PDF para imagens${NC}\n"
        continue
    fi

    echo -e "${GREEN}   ✅ $page_count imagem(ns) gerada(s)${NC}"
    echo -e "   🔍 Iniciando OCR (idioma: $LANG)...\n"

    # Adiciona título ao documento (primeira linha da primeira página)
    FIRST_PAGE=true
    PAGE_NUM=1

    # Processa cada página
    for img_file in "$TEMP_DIR"/page*.png; do
        [ -e "$img_file" ] || continue

        echo -e "   📖 Página $PAGE_NUM/$page_count:"
        echo -e "      🔍 Fazendo OCR..."

        # Faz OCR
        text_file="$TEMP_DIR/page_$PAGE_NUM.txt"
        if tesseract "$img_file" "${text_file%.txt}" -l "$LANG" --psm 6 2>/dev/null; then
            if [ -f "$text_file" ]; then
                # Conta caracteres
                char_count=$(wc -c < "$text_file" | tr -d ' ')

                if [ "$char_count" -gt 10 ]; then
                    echo -e "${GREEN}      ✅ Extraído: $char_count caracteres${NC}"

                    # Adiciona cabeçalho de página
                    if [ "$page_count" -gt 1 ]; then
                        if [ "$FIRST_PAGE" = true ]; then
                            # Primeira linha como título
                            first_line=$(head -1 "$text_file" | tr -d '\r')
                            if [ -n "$first_line" ]; then
                                echo "# $first_line" >> "$output_md"
                                echo "" >> "$output_md"
                            fi
                        fi

                        echo "## Página $PAGE_NUM" >> "$output_md"
                        echo "" >> "$output_md"
                    fi

                    # Adiciona conteúdo
                    if [ "$FIRST_PAGE" = true ]; then
                        # Remove primeira linha (já usada como título)
                        tail -n +2 "$text_file" >> "$output_md"
                    else
                        cat "$text_file" >> "$output_md"
                    fi

                    echo "" >> "$output_md"

                    # Adiciona separador entre páginas
                    if [ "$PAGE_NUM" -lt "$page_count" ]; then
                        echo "---" >> "$output_md"
                        echo "" >> "$output_md"
                    fi

                    # Preview
                    preview=$(head -c 80 "$text_file" | tr '\n' ' ')
                    echo -e "      💬 Preview: $preview..."

                    FIRST_PAGE=false
                else
                    echo -e "${YELLOW}      ⚠️ Nenhum texto detectado${NC}"
                fi
            fi
        else
            echo -e "${RED}      ❌ Erro no OCR${NC}"
        fi

        echo ""
        PAGE_NUM=$((PAGE_NUM + 1))
    done

    # Verifica se o arquivo MD foi criado com conteúdo
    if [ -s "$output_md" ]; then
        file_size=$(wc -c < "$output_md" | tr -d ' ')
        echo -e "${GREEN}✅ Conversão concluída!${NC}"
        echo -e "${GREEN}📁 Salvo em: $output_md${NC}"
        echo -e "${GREEN}📊 Tamanho: $file_size bytes${NC}\n"
        SUCCESS_FILES=$((SUCCESS_FILES + 1))
    else
        echo -e "${RED}❌ Falha: Arquivo vazio${NC}\n"
        rm -f "$output_md"
    fi

    # Limpa imagens temporárias
    rm -f "$TEMP_DIR"/page*.png
    rm -f "$TEMP_DIR"/page*.txt
done

# Resumo final
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 Conversão finalizada!${NC}"
echo -e "${GREEN}✅ $SUCCESS_FILES/$TOTAL_FILES arquivo(s) convertido(s) com sucesso${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

if [ "$SUCCESS_FILES" -gt 0 ]; then
    echo -e "${CYAN}Arquivos gerados:${NC}"
    for md_file in "$PDF_DIR"/*.md; do
        [ -e "$md_file" ] || continue
        size=$(wc -c < "$md_file" | tr -d ' ')
        echo -e "  ${GREEN}•${NC} $(basename "$md_file") (${size} bytes)"
    done
    echo ""
fi
