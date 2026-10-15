import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import publish_blogger as uploader


class BloggerSafetyTests(unittest.TestCase):
    def http_error(self, payload):
        return HTTPError(uploader.TOKEN_URL, 400, 'SECRET_REASON', {}, io.BytesIO(json.dumps(payload).encode()))

    def test_oauth_error_is_actionable_without_echoing_secrets(self):
        error = self.http_error({'error': 'invalid_grant', 'error_description': 'REFRESH_TOKEN_SECRET'})
        with patch.object(uploader, 'urlopen', side_effect=error):
            with self.assertRaises(RuntimeError) as caught:
                uploader.request_json(uploader.TOKEN_URL, method='POST', form=True, data={'refresh_token': 'TOKEN_SECRET'})
        result = str(caught.exception)
        self.assertIn('oauth_token_refresh failed: HTTP 400; code=invalid_grant', result)
        self.assertNotIn('SECRET', result)
        self.assertNotIn('https:', result)

    def test_arbitrary_error_code_is_not_logged(self):
        error = self.http_error({'error': 'SECRET_TOKEN', 'message': 'PRIVATE_DATA'})
        self.assertIn('code=unclassified', str(uploader.safe_http_error(error, uploader.TOKEN_URL, 'POST')))

    def test_api_reason_is_allowlisted(self):
        error = self.http_error({'error': {'status': 'INVALID_ARGUMENT', 'message': 'SECRET'}})
        message = str(uploader.safe_http_error(error, uploader.API, 'GET'))
        self.assertIn('blogger_api failed: HTTP 400; code=INVALID_ARGUMENT', message)
        self.assertNotIn('SECRET', message)

    def test_non_json_error_body_is_not_echoed(self):
        error = HTTPError(uploader.TOKEN_URL, 400, 'SECRET', {}, io.BytesIO(b'<html>SECRET</html>'))
        self.assertIn('code=unclassified', str(uploader.safe_http_error(error, uploader.TOKEN_URL, 'POST')))

    def test_live_match_stops_before_any_write(self):
        with patch.object(uploader, 'parse_post', return_value=('Title', 'Body', 'marker')):
            with patch.object(uploader, 'all_posts', return_value=iter([{'title': 'Title'}])):
                with patch.object(uploader, 'request_json') as request:
                    with self.assertRaisesRegex(ValueError, 'Matching live article'):
                        uploader.upload('source.html', '123', 'secret')
        request.assert_not_called()

    def test_create_requires_draft_and_readback(self):
        with patch.object(uploader, 'parse_post', return_value=('Title', 'Body', 'marker')):
            with patch.object(uploader, 'all_posts', return_value=iter([])):
                with patch.object(uploader, 'request_json', side_effect=[{'id': '456', 'status': 'DRAFT'}, {'id': '456', 'status': 'DRAFT'}]) as request:
                    uploader.upload('source.html', '123', 'secret')
        self.assertTrue(request.call_args_list[0].args[0].endswith('?isDraft=true'))
        self.assertEqual(request.call_args_list[0].kwargs['method'], 'POST')
        self.assertTrue(request.call_args_list[1].args[0].endswith('/456?view=ADMIN'))


if __name__ == '__main__':
    unittest.main()
