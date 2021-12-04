from requests import session
from pprint import pprint
from surugaya_parser import Search, SearchDetail, SearchDetailShort, KaitoriSearch, KaitoriSearchDetail
import sys

s = session()

# 販売一覧
#pg = Search(s, '11', 'めらみぽっぷ')
#pprint(pg.items)

# 販売詳細
#pgd = SearchDetail(s, '186125780')
#pprint(pgd.item)

# Search by circle or keyword
# Returns:
#choice = input("Enter c to search by circle or k for keyword: ")
#if (choice == 'c'):
#    restrict = input("Enter circle name: ")
#    pg = Search(s, '11', restrict)
#elif (choice == 'k'):
#    search_term = input("Enter search term: ")
#    pg = Search(s, '11', search_term)
#else:
#    sys.exit('baka')
#
#print("Results:", len(pg.items))
#
#for Item in pg.items:
#    code = Item.code
#    pgd = SearchDetail(s, code)
#    pprint(pgd.item)

# Search by circle or keyword. Selected attributes only, formatted.
# Returns: title, circle, release date, catalog
# Format: [release_date] title - circle {catalog}
choice = input('Enter c to search by circle or k for keyword: ')
if (choice == 'c'):
    brand = input('Enter circle name. Requires exact match e.g., "Foreground Eclipse" not "foreground eclipse."\n')
    pg = Search(s, '11', '', brand)
elif (choice == 'k'):
    search_term = input('Enter search term: ')
    pg = Search(s, '11', search_term)
else:
    sys.exit('baka')

print("Results:", len(pg.items))

for Item in pg.items:
    code = Item.code
    pgd = SearchDetailShort(s, code)
    release_date = pgd.item.release_date
    model_number = pgd.item.model_number
    if (release_date is None):
        release_date = 'Unknown'
    if (model_number is None):
        model_number = 'Unknown'
    print('[' + release_date + '] ' + pgd.item.brand + ' - ' + pgd.item.title + '{' + model_number + '}')


# 買取一覧
#kpg = KaitoriSearch(s, '11', '艦隊これくしょん かげぬい')
#pprint(kpg.items)

# 買取詳細
#kpgd = KaitoriSearchDetail(s, 'ZHORE150594')
#pprint(kpgd.item)
