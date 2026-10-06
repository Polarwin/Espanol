import argparse
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import subtitle_reading as app


class ReadingTests(unittest.TestCase):
    def test_translation_number_feedback(self):
        with self.assertRaisesRegex(ValueError, r"Missing: \['48,43'\]; unexpected: \['49'\]"):
            app.validate_translation({'translation': 'word ' * 60 + '49'}, 'palabra ' * 60 + '48,43')
        app.validate_translation({'translation': 'word ' * 60 + '48,43'}, 'palabra ' * 60 + '48,43')

    def test_rolling_vtt(self):
        first = ' '.join('palabra'+str(n) for n in range(35))
        raw = f'WEBVTT\n\n00:00:00.000 --> 00:00:02.000\n<c>{first}</c>\n\n00:00:02.000 --> 00:00:04.000\n{first} nueva &amp; final\n'
        self.assertEqual(app.clean_subtitles(raw), first+' nueva & final')

    def test_srt_and_time_selection(self):
        text = ' '.join('palabra'+str(n) for n in range(35))
        raw = f'1\n00:00:01,000 --> 00:00:03,000\nFUERA\n\n2\n00:00:10,000 --> 00:00:12,000\n{text}\n'
        self.assertEqual(app.clean_subtitles(raw, 5, 10), text)
        with self.assertRaises(ValueError):
            app.clean_subtitles(raw, 30, 5)

    def test_url_candidates_keep_encoding_query(self):
        value = app.candidates('https://host/video%20uno.mp4?v=123')[0]
        self.assertEqual(value, 'https://host/video%20uno.es-orig.vtt?v=123')

    def test_srt_repeated_speech_is_preserved(self):
        words = ' '.join(['hola']*20)
        raw = f'1\n00:00:01,000 --> 00:00:03,000\n{words}\n\n2\n00:00:03,000 --> 00:00:05,000\n{words}\n'
        self.assertEqual(app.clean_subtitles(raw), words+' '+words)

    def test_known_lan_url_maps_to_local_subtitles(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            text = 'WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nHola.'
            (root/'Vídeo uno.es-orig.vtt').write_text(text)
            args = argparse.Namespace(media_root=root, insecure=False)
            with patch.object(app, 'urlopen', side_effect=AssertionError('Must not use network')):
                raw, source = app.fetch_subtitles('https://192.168.0.9/ytwatcher/V%C3%ADdeo%20uno.mp4?v=3', args)
            self.assertEqual(raw, text)
            self.assertTrue(source.endswith('Vídeo uno.es-orig.vtt'))

    def test_path_traversal_rejected(self):
        args = argparse.Namespace(media_root=Path('/srv/files/ytwatcher'), insecure=False)
        with self.assertRaises(ValueError):
            app.fetch_subtitles('https://192.168.0.9/ytwatcher/%2e%2e/private.vtt', args)

    def pack(self):
        return {'title':'Noticias', 'reading':'Ana vive en Brasil.', 'source':'<script>alert(1)</script>',
                'start':0, 'duration':300, 'level':'A2',
                'translation':'Ana lives in Brazil.',
                'questions':[{'question':'¿Dónde vive Ana?', 'suggested_answer':'Ana vive en Brasil, según el texto.'}],
                'vocabulary':[{'term':'vive','spanish':'Tiene su casa en un lugar.','english':'Lives; has a home in a place.'}]}

    def test_validation_and_separate_answers(self):
        pack = self.pack()
        app.validate_tasks(pack, pack['reading'], 1, 1)
        pages = app.render(pack)
        self.assertNotIn('Ana vive en Brasil, según el texto.', pages['ejercicio.html'])
        self.assertIn('Ana vive en Brasil, según el texto.', pages['respuestas.html'])
        self.assertIn('class="supplement answers"', pages['imprimir.html'])
        self.assertIn('break-before:page', pages['imprimir.html'])
        self.assertNotIn('<script>', pages['ejercicio.html'])
        self.assertIn('Lives; has a home', pages['ejercicio.html'])

    def test_invalid_answer_evidence_vocabulary(self):
        for field, bad in [('suggested_answer',''), ('options',['A','B','C'])]:
            pack = self.pack()
            pack['questions'][0][field] = bad
            with self.assertRaises(ValueError):
                app.validate_tasks(pack, pack['reading'], 1, 1)
        pack = self.pack()
        pack['vocabulary'][0]['term']='elecciones'
        with self.assertRaises(ValueError):
            app.validate_tasks(pack, pack['reading'], 1, 1)

    def test_chat_retries_invalid_structure(self):
        args = argparse.Namespace(model='local-test', api='http://localhost:8349/v1', timeout=10)
        good = {'title':'Título', 'reading':' '.join(['palabra']*120)}
        def response(value):
            return io.BytesIO(json.dumps({'choices':[{'finish_reason':'stop','message':{'content':json.dumps(value)}}]}).encode())
        with patch.object(app, 'urlopen', side_effect=[response({}), response(good)]) as mocked:
            result = app.chat(args, 'Genera una lectura.', 'subtítulos', app.validate_reading)
        self.assertEqual(result, good)
        self.assertEqual(mocked.call_count, 2)

    def test_chat_rejects_truncation(self):
        args = argparse.Namespace(model='local-test', api='http://localhost:8349/v1', timeout=10)
        def response(*args, **kwargs):
            return io.BytesIO(b'{"choices":[{"finish_reason":"length","message":{"content":"{}"}}]}')
        with patch.object(app, 'urlopen', side_effect=response), self.assertRaises(ValueError):
            app.chat(args, 'Genera una lectura.', 'subtítulos', app.validate_reading)

    def test_strict_schema_limits_counts_and_evidence(self):
        schema = app.tasks_schema('Ana vive en Brasil. Tiene dos hijos.', 5, 8)
        self.assertFalse(schema['additionalProperties'])
        questions = schema['properties']['questions']
        self.assertEqual((questions['minItems'],questions['maxItems']),(5,5))
        self.assertIn('suggested_answer', questions['items']['properties'])
        self.assertNotIn('answer', questions['items']['properties'])
        self.assertEqual(schema['properties']['vocabulary']['maxItems'],8)

    def test_invented_numbers_rejected(self):
        reading = {'title':'Noticias','reading':' '.join(['palabra']*100)+' 55 millones.'}
        with self.assertRaises(ValueError):
            app.validate_reading(reading,'56 millones y el 45 por ciento.')

    def test_repeated_term_is_not_a_definition(self):
        pack = self.pack()
        pack['vocabulary'][0]['spanish']='vive'
        with self.assertRaises(ValueError):
            app.validate_tasks(pack, pack['reading'], 1, 1)

    def test_vocabulary_schema_preserves_word_sense(self):
        schema = app.tasks_schema('La inseguridad preocupa a los votantes.',1,1)
        terms = schema['properties']['vocabulary']['items']['properties']['term']['enum']
        self.assertIn('inseguridad',terms)
        self.assertNotIn('seguridad',terms)

    def test_translation_separate_and_escaped(self):
        pack = self.pack()
        pack['translation'] = 'ENGLISH SECRET <script>bad</script>\n\nSecond paragraph.'
        pages = app.render(pack)
        self.assertNotIn('ENGLISH SECRET',pages['ejercicio.html'])
        self.assertNotIn('ENGLISH SECRET',pages['respuestas.html'])
        self.assertIn('ENGLISH SECRET',pages['traduccion.html'])
        self.assertIn('&lt;script&gt;',pages['traduccion.html'])
        self.assertIn('<p>Second paragraph.</p>',pages['traduccion.html'])
        self.assertEqual(pages['imprimir.html'].count('<section class="supplement'),2)

    def test_chunks_preserve_unicode_and_long_sentences(self):
        text = ('Una oración sobre España. ' + 'áéíóú y Brasil '*30)*8
        chunks = app.split_chunks(text,180)
        self.assertEqual(''.join(chunks),text)
        self.assertGreater(len(chunks),1)
        self.assertTrue(all(len(c.encode('utf-8'))<=180 for c in chunks))

    def test_summary_processes_every_chunk(self):
        args = argparse.Namespace(context_size=8192,max_output_tokens=2000,context_margin=512,max_source_chars=700)
        text = 'España tiene varias ciudades. '*150
        expected = app.split_chunks(text,700)
        seen=[]
        def fake_chat(args,instruction,data,validate,schema,max_tokens=None):
            seen.append(data)
            result={'summary':'Resumen breve de este fragmento sobre las ciudades de España.'}
            validate(result)
            return result
        with patch.object(app,'chat',side_effect=fake_chat):
            condensed,audit=app.prepare_context(text,args)
        self.assertEqual(seen,expected)
        self.assertEqual(len(audit),len(expected))
        self.assertLessEqual(len(condensed.encode('utf-8')),700)

    def test_context_guard_prevents_request(self):
        args=argparse.Namespace(model='local',api='http://localhost/v1',timeout=10,context_size=1024,max_output_tokens=500,context_margin=128)
        with patch.object(app,'urlopen') as network, self.assertRaises(ValueError):
            app.chat(args,'Task','x'*3000,lambda v:None)
        network.assert_not_called()

    def test_short_source_needs_no_summary(self):
        args=argparse.Namespace(context_size=8192,max_output_tokens=2000,context_margin=512,max_source_chars=11000)
        with patch.object(app,'chat') as model:
            self.assertEqual(app.prepare_context('Texto corto.',args),('Texto corto.',[]))
        model.assert_not_called()

    def test_hierarchical_summaries(self):
        args=argparse.Namespace(context_size=8192,max_output_tokens=2000,context_margin=512,max_source_chars=700)
        def fake(*a,**kw):
            return {'summary':'Resumen de una noticia en español. '*5}
        with patch.object(app,'chat',side_effect=fake):
            result,audit=app.prepare_context('Una noticia de España. '*400,args)
        self.assertLessEqual(len(result.encode()),700)
        self.assertGreater(max(x['level'] for x in audit),1)

    def test_end_to_end_generation_with_mock_model(self):
        with TemporaryDirectory() as directory:
            root=Path(directory)
            source=root/'video.es.vtt'
            source.write_text('WEBVTT\n\n00:00:00.000 --> 00:01:00.000\n'+'Una palabra sobre España. '*300)
            output=root/'output'
            seen=[]
            def fake(args,instruction,data,validate,schema,max_tokens=None):
                seen.append(instruction)
                if instruction.startswith('Resume'):
                    value={'summary':'Una palabra permite expresar una idea en español.'}
                elif instruction.startswith('Crea una lectura'):
                    value={'title':'Una lectura', 'reading':'palabra '*110}
                elif instruction.startswith('Traduce'):
                    value={'translation':'word '*110}
                else:
                    value={'questions':[{'question':'¿Qué aparece?', 'suggested_answer':'Aparece una palabra.'}],
                           'vocabulary':[{'term':'palabra','spanish':'Unidad que permite expresar una idea.','english':'A unit of language that expresses meaning.'}]}
                validate(value)
                return value
            with patch('sys.argv',['script',str(source),'--output',str(output),'--questions','1','--vocabulary','1']), patch.object(app,'chat',side_effect=fake):
                app.main()
            self.assertTrue(any(s.startswith('Resume') for s in seen))
            pack=json.loads((output/'ejercicio.json').read_text())
            self.assertEqual(pack['review_status'],'draft')
            self.assertGreater(pack['summary_chunks'],0)
            self.assertTrue((output/'traduccion.html').exists())
            self.assertNotIn('word word', (output/'ejercicio.html').read_text())
            self.assertEqual((output/'subtitulos.txt').read_text().count('Una palabra'),300)


if __name__ == '__main__':
    unittest.main()
