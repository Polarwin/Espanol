export type Edit = { kind: 'same' | 'removed' | 'added'; text: string }

// Preserve word boundaries, spelling, accents and punctuation. Only normalize
// spacing that cannot turn one word into another ("a ver" is not "aver").
function normalizeSpacing(text: string): string {
  return text.replace(/\s+/gu, ' ').trim()
    .replace(/\s*([.,;:!?…¿¡()[\]«»])\s*/gu, '$1')
}

export function correctionKind(original: string, suggested: string): 'unchanged' | 'spacing' | 'text' {
  if (original === suggested) return 'unchanged'
  return normalizeSpacing(original) === normalizeSpacing(suggested) ? 'spacing' : 'text'
}

export function writingDiff(original: string, suggested: string): Edit[] {
  const tokens = (text: string) => text.match(/\s+|[\p{L}\p{M}\p{N}]+|[^\s]/gu) ?? []
  const before = tokens(original)
  const after = tokens(suggested)
  const edits: Edit[] = []
  function append(kind: Edit['kind'], text: string) {
    if (!text) return
    const last = edits.at(-1)
    if (last?.kind === kind) last.text += text
    else edits.push({ kind, text })
  }
  // Bound memory/work for long, punctuation-heavy input. The fallback still
  // reconstructs both texts exactly, highlighting the changed middle span.
  if (before.length * after.length > 1_000_000) {
    let start = 0
    while (start < before.length && start < after.length && before[start] === after[start]) start++
    let endBefore = before.length
    let endAfter = after.length
    while (endBefore > start && endAfter > start && before[endBefore - 1] === after[endAfter - 1]) { endBefore--; endAfter-- }
    append('same', before.slice(0, start).join(''))
    append('removed', before.slice(start, endBefore).join(''))
    append('added', after.slice(start, endAfter).join(''))
    append('same', before.slice(endBefore).join(''))
    return edits
  }
  const width = after.length + 1
  const lengths = new Uint32Array((before.length + 1) * width)
  for (let i = before.length - 1; i >= 0; i--) {
    for (let j = after.length - 1; j >= 0; j--) {
      lengths[i * width + j] = before[i] === after[j]
        ? 1 + lengths[(i + 1) * width + j + 1]
        : Math.max(lengths[(i + 1) * width + j], lengths[i * width + j + 1])
    }
  }
  let i = 0
  let j = 0
  while (i < before.length || j < after.length) {
    if (i < before.length && j < after.length && before[i] === after[j]) {
      append('same', before[i]); i++; j++
    } else if (i < before.length && (j === after.length || lengths[(i + 1) * width + j] >= lengths[i * width + j + 1])) {
      append('removed', before[i++])
    } else append('added', after[j++])
  }
  return edits
}

export function visibleSpaces(text: string): string {
  return text.replace(/ /g, '␠').replace(/\t/g, '⇥').replace(/\r?\n/g, '↵\n')
}
