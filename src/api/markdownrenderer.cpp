/**********************************************************************
 * File:        markdownrenderer.cpp
 * Description: Simple API for rendering tesseract output as Markdown
 * Author:      Claude AI Assistant
 *
 * (C) Copyright 2026
 ** Licensed under the Apache License, Version 2.0 (the "License");
 ** you may not use this file except in compliance with the License.
 ** You may obtain a copy of the License at
 ** http://www.apache.org/licenses/LICENSE-2.0
 ** Unless required by applicable law or agreed to in writing, software
 ** distributed under the License is distributed on an "AS IS" BASIS,
 ** WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 ** See the License for the specific language governing permissions and
 ** limitations under the License.
 *
 **********************************************************************/

#include <memory>     // for std::unique_ptr
#include <sstream>    // for std::stringstream
#include <string>     // for std::string
#include "baseapi.h"  // for TessBaseAPI
#include "renderer.h"

namespace tesseract {

/**********************************************************************
 * Markdown Text Renderer implementation
 **********************************************************************/
TessMarkdownRenderer::TessMarkdownRenderer(const char *outputbase)
    : TessResultRenderer(outputbase, "md") {
}

bool TessMarkdownRenderer::BeginDocumentHandler() {
  // Add markdown document header
  if (!title().empty()) {
    std::stringstream header;
    header << "# " << title() << "\n\n";
    AppendString(header.str().c_str());
  }
  return true;
}

bool TessMarkdownRenderer::AddImageHandler(TessBaseAPI* api) {
  const std::unique_ptr<const char[]> utf8(api->GetUTF8Text());
  if (utf8 == nullptr) {
    return false;
  }

  // Add page header if there are multiple pages
  if (imagenum() > 0) {
    std::stringstream page_header;
    page_header << "\n---\n\n## Page " << (imagenum() + 1) << "\n\n";
    AppendString(page_header.str().c_str());
  } else if (imagenum() == 0 && !title().empty()) {
    // First page, add subheading
    AppendString("## Page 1\n\n");
  }

  // Process the text to improve markdown formatting
  std::string text(utf8.get());
  std::string formatted_text = FormatTextAsMarkdown(text);

  AppendString(formatted_text.c_str());

  // Add page separator
  const char* pageSeparator = api->GetStringVariable("page_separator");
  if (pageSeparator != nullptr && *pageSeparator != '\0') {
    AppendString(pageSeparator);
  } else {
    AppendString("\n");
  }

  return true;
}

bool TessMarkdownRenderer::EndDocumentHandler() {
  // Add footer if needed
  AppendString("\n");
  return true;
}

std::string TessMarkdownRenderer::FormatTextAsMarkdown(const std::string& text) {
  if (text.empty()) {
    return text;
  }

  std::stringstream result;
  std::istringstream stream(text);
  std::string line;
  std::string prev_line;
  bool in_paragraph = false;
  int empty_line_count = 0;

  while (std::getline(stream, line)) {
    // Trim trailing whitespace
    size_t end = line.find_last_not_of(" \t\r\n");
    if (end != std::string::npos) {
      line = line.substr(0, end + 1);
    } else {
      line = "";
    }

    // Handle empty lines
    if (line.empty()) {
      empty_line_count++;
      if (empty_line_count == 1 && in_paragraph) {
        result << "\n\n";
        in_paragraph = false;
      }
      continue;
    }

    // Reset empty line counter
    empty_line_count = 0;

    // Detect potential headings (lines that are short and in all caps or title case)
    bool is_potential_heading = false;
    if (line.length() < 60 && line.length() > 0) {
      // Check if line might be a heading (simple heuristic)
      size_t upper_count = 0;
      size_t alpha_count = 0;
      for (char c : line) {
        if (std::isalpha(c)) {
          alpha_count++;
          if (std::isupper(c)) {
            upper_count++;
          }
        }
      }
      // If more than 70% uppercase or starts with uppercase after whitespace
      if (alpha_count > 0 &&
          (upper_count * 100 / alpha_count > 70 ||
           (line[0] != ' ' && std::isupper(line[0])))) {
        is_potential_heading = true;
      }
    }

    // Format the line
    if (is_potential_heading && !in_paragraph) {
      // Don't add too many heading levels, use ### for sub-headings
      result << "### " << line << "\n\n";
      in_paragraph = false;
    } else {
      // Regular paragraph text
      if (!in_paragraph && !prev_line.empty()) {
        result << "\n";
      }
      result << line << "\n";
      in_paragraph = true;
    }

    prev_line = line;
  }

  return result.str();
}

}  // namespace tesseract
