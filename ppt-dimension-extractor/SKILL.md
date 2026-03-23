---
name: ppt-dimension-extractor
description: Extract teaching content from courseware files by following a user-provided dimension table or rubric, especially when the user gives an Excel/worksheet with categories and extraction rules plus a PPT/PPTX to analyze. Use this whenever the user wants you to map slide content into dimensions such as vocabulary, reading, phonics, grammar, sentence structures, or similar curriculum buckets, even if they do not explicitly ask for a "skill." Also use it when the user wants the extracted result filled into a new Excel workbook, wants unfound items left blank, wants a structured teaching-content summary generated from slide decks, or asks to use the built-in L4 teaching-dimension standard without re-uploading the Excel. When the input includes a PPT/PPTX, first use the PPTX skill workflow to turn the deck into per-slide images, then extract from both slide images and text together rather than relying on text alone.
---

# PPT Dimension Extractor

Extract teaching content from PPT/PPTX courseware according to a dimension table, rubric, or Excel specification supplied by the user.

## When to use
Use this skill when the user:
- provides a PPT/PPTX and a dimension table, rubric, or Excel file
- asks to extract teaching content into categories
- wants slide content reorganized by curriculum dimensions
- wants a result workbook produced from extracted findings
- wants missing or unfound items left blank instead of filled with placeholder text

## Inputs
Usually the user provides:
1. A dimension source, often an Excel file, that contains:
   - dimension names
   - extraction standards or rules
2. A PPT/PPTX courseware file to analyze
3. Optional output preferences, such as:
   - summary in chat
   - new Excel workbook
   - blank cells for unfound items
   - title or filename requirements

If the user is working on **L4 teaching-content extraction** and does not provide a new Excel in the current request, read `references/l4-dimensions.md` and use that built-in rubric as the default reference.

## Required PPT handling
When the input includes a PPT/PPTX, do not rely on plain text extraction alone.

You must explicitly invoke the existing `pptx` skill workflow as the PPT processing layer before doing dimension extraction.

Required order:
1. use the `pptx` skill workflow to extract slide text
2. use the `pptx` skill workflow to convert the deck into one image per slide
3. inspect slide images and extracted text together
4. only then map content into dimensions

Treat the slide images as mandatory evidence, not an optional fallback. The goal is to catch color-based cues, upper-right labels, layout-specific prompts, red-font targets, and other visual signals that plain text extraction can miss.

If the task involves PPT/PPTX and you skip the PPT skill workflow, the extraction is incomplete.

### Failure fallback rules
- If text extraction succeeds but slide-image conversion fails, do not declare the task complete. Keep trying alternate workable methods until slide images are available.
- If slide-image conversion succeeds but text extraction is partial or poor, continue with image-led extraction and use whatever text evidence is available.
- If both text extraction and image conversion fail on the first attempt, switch methods and retry. Do not stop at the first failure.
- If visual evidence is available, never downgrade to text-only extraction just because text is easier to parse.
- Only report limitation or uncertainty after exhausting practical ways to obtain real slide text and slide images.

## Core workflow

### 1. Read the requirement source first
If the user provides an Excel, rubric, or table describing dimensions and extraction standards, read that before extracting from the PPT.

If the task is clearly about **L4** and no new rule file is provided, read `references/l4-dimensions.md` and use the built-in L4 dimensions.

Priority order:
1. the user's current Excel or rubric
2. the built-in L4 reference when the task explicitly or implicitly targets L4
3. only ask for clarification when neither exists and the expected rubric is genuinely ambiguous

Goal: understand exactly what counts for each dimension. Do not guess from the dimension name alone.

Capture at least:
- dimension name
- extraction rule
- expected output granularity
- whether empty results should be blank or labeled

### 2. Read and inspect the PPT/PPTX
Extract usable content from the slide deck.

For PPT/PPTX inputs, first follow the `pptx` skill's reading workflow so you have both:
- text extracted from the PPT
- one image per slide converted from the deck

Then do multimodal extraction from both sources together. Do not make dimension judgments from text alone when slide images are available.

What to capture from slides:
- page titles
- visible words or phrases
- reading passages
- questions
- phonics targets
- grammar examples
- sentence patterns
- math items if present
- any signals like section labels such as Engage, Explore, Let’s Talk, Reader Detective, Vocabulary, Phonics, Grammar, Explain, Extend
- red-font targets, option words, and page labels visible only through slide images

For the built-in L4 rubric, pay special attention to the page labels in the upper-right area and match them carefully against Engage / Explore / Explain / Extend before assigning content to a dimension.

If text extraction and slide-image evidence disagree, prefer the combined interpretation grounded in the actual slide visuals. Mention uncertainty only when the visual evidence remains ambiguous.

If direct file reading is unsupported, use an alternate method that still gets real content from the files. Do not fabricate slide content.


### 3. Apply the rubric dimension by dimension
For each dimension:
- follow the extraction standard literally
- include only content that matches that standard
- keep the result concise but complete enough for reuse
- if nothing is found, leave it empty when the user asked for blanks
- verify the extracted item against both slide text and slide image evidence before assigning it

Be careful not to mix neighboring categories. For example:
- titles are not full passages
- a vocabulary page is not automatically a phonics page
- questions after a reading belong to comprehension, not fluency
- text that appears in OCR or extracted text but is not visually part of the target page element should not be forced into the result

If color, placement, or page-region rules matter, use the slide images to decide. This is especially important for red-font words, upper-right page labels, option words, and question blocks.

### 4. Produce structured output
Default output structure:

## [Unit or file name]
### 1. [Dimension name]
- 提取标准: [rule]
- 提取结果: [content]

When the user wants a workbook, create a clean table with columns such as:
- 教学内容维度
- 提取标准
- 提取结果

If the request uses the built-in L4 rubric, keep the output order exactly as follows:
1. Content Vocab
2. Reading Fluency
3. Reading Comprehension
4. Verbs
5. Phonics
6. High Frequency Words
7. Sentence Structures
8. Grammar
9. Math

If the user wants unfound items blank:
- keep the result cell empty
- do not write “未找到”, “N/A”, or similar filler

## Output quality bar
- Be faithful to the supplied rubric.
- Separate extraction from interpretation.
- Preserve original wording when extracting slide text.
- Use Chinese explanations if the surrounding task is in Chinese.
- Prefer readable, teacher-friendly formatting.

## Handling missing-tool situations
If standard file-reading tools do not support the file types:
- switch to another workable method
- keep working until you can access real content
- do not claim a result based on assumptions

## Example use cases
- “根据这个 Excel 里的教学内容维度和提取标准，提取这个 PPT 的内容。”
- “把这个课件按 vocabulary / reading / grammar 分类整理出来。”
- “帮我把提取结果写成一个 Excel，未找到的项留空。”
- “按表格里的规则，把课件里的内容填进去。”

## Final answer style
Return:
1. the extracted structured result, or
2. a short completion message plus output file location if a workbook was created

Keep the answer direct and practical.
