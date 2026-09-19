import assert from 'node:assert/strict'
import test from 'node:test'
import { correctionKind, writingDiff, visibleSpaces } from '../src/components/writingDiff.ts'

test('classifies the reported spacing-only edit separately', () => {
  assert.equal(correctionKind('Me cuesta hablar español .', 'Me cuesta hablar español.'), 'spacing')
  assert.equal(correctionKind(' Me gusta  cocinar.\n', 'Me gusta cocinar.'), 'spacing')
  assert.equal(correctionKind('Hola,mundo.', 'Hola, mundo.'), 'spacing')
  assert.equal(correctionKind('Me gusta cocinar.', 'Me gusta cocinar.'), 'unchanged')
})

test('does not hide spelling, accents, punctuation or changed word boundaries as spacing', () => {
  for (const [before, after] of [['parcticar', 'practicar'], ['dia', 'día'], ['a ver', 'aver'],
    ['del', 'de el'], ['hola.', 'hola!'], ['Me gusta los libros.', 'Me gustan los libros.']]) {
    assert.equal(correctionKind(before, after), 'text')
  }
})

test('isolates both actual edits in the learner example', () => {
  const parts = writingDiff('Te recomiendo parcticar español cada dia.', 'Te recomiendo practicar español cada día.')
  assert.deepEqual(parts.filter(part => part.kind === 'removed').map(part => part.text), ['parcticar', 'dia'])
  assert.deepEqual(parts.filter(part => part.kind === 'added').map(part => part.text), ['practicar', 'día'])
})

test('diff reconstructs originals and suggestions, including repeated words and bounded fallback', () => {
  for (const [before, after] of [['español .', 'español.'], ['hola hola mundo', 'hola mundo'],
    ['', 'Hola'], ['Hola', ''], ['¿Qué tal?', '¿Qué tal?'], ['<script>', '<span>'],
    ['! '.repeat(1200) + 'antes', '! '.repeat(1200) + 'después']]) {
    const parts = writingDiff(before, after)
    assert.equal(parts.filter(part => part.kind !== 'added').map(part => part.text).join(''), before)
    assert.equal(parts.filter(part => part.kind !== 'removed').map(part => part.text).join(''), after)
  }
  assert.equal(visibleSpaces(' \t\n'), '␠⇥↵\n')
})
