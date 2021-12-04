# surugaya_parser
Updated version following updates to suruga-ya.jp around April 2021. Repaired and revised functionality.

Functions updated: Search, SearchDetail. Function added: SearchDetailShort. Updated parsing for compatibility with the new page structure.

General: added ability to search by "brand" or circle name. Improved handling of title strings and URL encoding.

Not updated: KaitoriSearch, KaitoriSearchDetail


Get list of search results (example in example.py)

```
# Search
pg = Search(s, '11', 'Foreground Eclipse')
pprint(pg.items)
```

Get item details from search (example in example.py)

```
# SearchDetail
pgd = SearchDetail(s, '186125780')
pprint(pgd.item)
```

Get specific attributes from circle or keyword search. The main update: SearchDetailShort.

Returns: title, circle, release date, catalog.

Format: [release_date] title - circle {catalog}
