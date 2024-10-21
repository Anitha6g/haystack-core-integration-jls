##### Haystack Implementation ######
# SPDX-FileCopyrightText: 2023-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any, Dict, List, Optional, Union
from haystack import Document, component, default_from_dict, default_to_dict
from haystack.utils import Secret, deserialize_secrets_inplace
from .mode import JinaReaderMode
import requests
import urllib

@component
class JinaReader():

    def __init__(
        self,
        mode: Union[JinaReaderMode, str],
        url: Optional[str] = None,
        reader_query: Optional[str] = None,
        api_key: Secret = Secret.from_env_var("JINA_API_KEY"),
    ):

        resolved_api_key = api_key.resolve_value()
        self.api_key = api_key
        self.mode = mode
        self.url = url
        self.reader_query = reader_query

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {resolved_api_key}",
                "Accept-Encoding": "identity",
                "Content-type": "application/json",
            }
        )

    @component.output_types(document=Document)
    def run(self, input:str):

        # check input depending on mode
        mode_map = {
            JinaReaderMode.READ: "r",
            JinaReaderMode.SEARCH: "s",
            JinaReaderMode.GROUND: "g"
        }
        base_url = "https://{}.jina.ai/".format(mode_map[self.mode])
        encoded_target = urllib.parse.quote(input, safe="")
        url = f"{base_url}{encoded_target}"
        response = self._session.get(
            url
        )
        metadata = {
            'content_type': response.headers['Content-Type'],
            'url':input
            }
        document = [Document(content = response.content, meta = metadata)]
        return document

        ... # do the rest and clean ups
        