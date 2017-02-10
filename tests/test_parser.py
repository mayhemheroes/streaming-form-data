from unittest import TestCase

from requests_toolbelt import MultipartEncoder
from streaming_form_data.parser import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget
from streaming_form_data.part import Part


class StreamingFormDataParserTestCase(TestCase):
    def test_smoke(self):
        encoder = MultipartEncoder(fields={'name': 'hello'})

        parser = StreamingFormDataParser(
            expected_parts=(), headers={'Content-Type': encoder.content_type})
        parser.data_received(encoder.to_string())

    def test_basic_single(self):
        target = ValueTarget()
        expected_parts = (Part('value', target),)

        encoder = MultipartEncoder(fields={'value': 'hello world'})

        parser = StreamingFormDataParser(
            expected_parts=expected_parts,
            headers={'Content-Type': encoder.content_type})
        parser.data_received(encoder.to_string())

        self.assertEqual(target.value, b'hello world')

    def test_basic_multiple(self):
        first = ValueTarget()
        second = ValueTarget()
        third = ValueTarget()

        expected_parts = (
            Part('first', first),
            Part('second', second),
            Part('third', third),
        )

        encoder = MultipartEncoder(fields={
            'first': 'foo',
            'second': 'bar',
            'third': 'baz'
        })

        parser = StreamingFormDataParser(
            expected_parts=expected_parts,
            headers={'Content-Type': encoder.content_type})
        parser.data_received(encoder.to_string())

        self.assertEqual(first.value, b'foo')
        self.assertEqual(second.value, b'bar')
        self.assertEqual(third.value, b'baz')

    def test_chunked_single(self):
        expected_value = 'hello' * 5000

        target = ValueTarget()
        expected_parts = (Part('value', target),)

        encoder = MultipartEncoder(fields={'value': expected_value})

        body = encoder.to_string()

        parser = StreamingFormDataParser(
            expected_parts=expected_parts,
            headers={'Content-Type': encoder.content_type})

        chunks = []
        size = 500

        while len(body):
            chunks.append(body[:size])
            body = body[size:]

        for chunk in chunks:
            parser.data_received(chunk)

        self.assertEqual(target.value, expected_value.encode('utf-8'))

    def test_chunked_multiple(self):
        expected_first_value = 'foo' * 5000
        expected_second_value = 'bar' * 5000
        expected_third_value = 'baz' * 5000

        first = ValueTarget()
        second = ValueTarget()
        third = ValueTarget()

        expected_parts = (
            Part('first', first),
            Part('second', second),
            Part('third', third),
        )

        encoder = MultipartEncoder(fields={
            'first': expected_first_value,
            'second': expected_second_value,
            'third': expected_third_value,
        })

        body = encoder.to_string()

        parser = StreamingFormDataParser(
            expected_parts=expected_parts,
            headers={'Content-Type': encoder.content_type})

        chunks = []
        size = 500

        while len(body):
            chunks.append(body[:size])
            body = body[size:]

        for chunk in chunks:
            parser.data_received(chunk)

        self.assertEqual(first.value, expected_first_value.encode('utf-8'))
        self.assertEqual(second.value, expected_second_value.encode('utf-8'))
        self.assertEqual(third.value, expected_third_value.encode('utf-8'))

    def test_break_chunk_at_boundary(self):
        expected_first_value = 'hello' * 500
        expected_second_value = 'hello' * 500

        first = ValueTarget()
        second = ValueTarget()

        expected_parts = (
            Part('first', first),
            Part('second', second),
        )

        encoder = MultipartEncoder(fields={
            'first': 'hello' * 500,
            'second': 'hello' * 500
        })

        body = encoder.to_string()
        boundary = encoder.boundary.encode('utf-8')

        parser = StreamingFormDataParser(
            expected_parts=expected_parts,
            headers={'Content-Type': encoder.content_type})

        index = body[50:].index(boundary) + 5

        parser.data_received(body[:index])
        parser.data_received(body[index:])

        self.assertEqual(first.value, expected_first_value.encode('utf-8'))
        self.assertEqual(second.value, expected_second_value.encode('utf-8'))