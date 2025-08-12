from typing import Dict, Optional
import requests
from src.backend.clients.http_client import HTTPClient


class CatalogAdapter:
    def __init__(self, client: HTTPClient) -> None:
        self.client = client

    def get_catalog(
        self,
        token: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        brand: Optional[str] = None,
    ) -> requests.Response:
        params: Dict[str, str] = {}
        if min_price is not None:
            params['min_price'] = str(min_price)
        if max_price is not None:
            params['max_price'] = str(max_price)
        if brand is not None:
            params['brand'] = brand
        if sort_by is not None:
            if sort_by == 'price':
                params['sort'] = 'price_asc' if sort_order == 'asc' else 'price_desc'
            elif sort_by == 'name':
                params['sort'] = 'name_asc' if sort_order == 'asc' else 'name_desc'
        headers = {'Authorization': token} if token else None
        return self.client.get('/catalog/', headers=headers, params=params or None)
