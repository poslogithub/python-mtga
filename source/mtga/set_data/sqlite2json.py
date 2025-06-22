import sqlite3
from locale import getlocale


class Table():
    ABILITIES = 'Abilities'
    CARDS = 'Cards'
    LOCALIZATIONS = 'Localizations'
    ENUMS = 'Enums'

class Column():
    CID = 0
    NAME = 1
    TYPE = 2
    NOTNULL = 3
    DEFAULT_VALUE = 4
    PRIMARY_KEY = 5

class Row():
    LOC_ID = 'LocId'
    FORMATTED = 'Formatted'
    LOC = 'Loc'
    TYPE = 'Type'

class Key():
    ID = 'id'
    TEXT = 'text'
    NAME = 'name'
    VALUES = 'values'

ISO_CODE = {
    'English': 'enUS',
    'Portuguese': 'ptBR',
    'French': 'frFR',
    'Italian': 'itIT',
    'German': 'deDE',
    'Spanish': 'esES',
    'Castilian': 'esES',
    'Russian': 'ruRU',
    'Japanese': 'jaJP',
    'Korean': 'koKR'
}    

ENUMS_TYPES = [
    'CardType',
    'Color',
    'CounterType',
    'FailureReason',
    'MatchState',
    'Phase',
    'ResultCode',
    'Step',
    'SubType',
    'SuperType'
]

def get_column_names(cur, table_name):
    rst = []
    cur.execute("PRAGMA table_info('"+table_name+"')")
    records = cur.fetchall()
    rst = [record[Column.NAME] for record in records]
    return rst

def sqlite2json(sqlite_filepath):
    abilities = []
    cards = []
    loc = []
    enums = []
    lang = getlocale()[0].split("_")[0]
    iso_code = ISO_CODE.get(lang) if ISO_CODE.get(lang) else ISO_CODE['English']

    try:
        con = sqlite3.connect(sqlite_filepath)
        cur = con.cursor()

        # Abilities
        column_names = get_column_names(cur, Table.ABILITIES)
        cur.execute("select * from "+Table.ABILITIES)
        records = cur.fetchall()
        for record in records:
            ability = {}
            for i in range(len(record)):
                ability[column_names[i]] = record[i]
            abilities.append(ability)

        # Cards
        column_names = get_column_names(cur, Table.CARDS)
        cur.execute("select * from "+Table.CARDS)
        records = cur.fetchall()
        for record in records:
            card = {}
            for i in range(len(record)):
                card[column_names[i]] = record[i]
            cards.append(card)

        # Localizations
        cur.execute("select "+Row.LOC_ID+", "+Row.LOC+" from "+Table.LOCALIZATIONS+"_"+iso_code.replace('_', '')+" where "+Row.FORMATTED+" = 1")
        records = cur.fetchall()
        for record in records:
            loc.append(
                {
                    Key.ID: record[0],
                    Key.TEXT: record[1]
                }
            )
        
        # Enums
        for type in ENUMS_TYPES:
            enums.append(
                {
                    Key.NAME: type,
                    Key.VALUES: []
                }
            )
            cur.execute("select * from "+Table.ENUMS+" where "+Row.TYPE+ " = '"+type+"'")
            records = cur.fetchall()
            for record in records:
                enums[-1][Key.VALUES].append(
                    {
                        Key.ID: record[1],
                        Key.TEXT: record[2]
                    }
                )
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if con:
            con.close()

    return abilities, cards, loc, enums

if __name__ == "__main__":
    from json import dump
    abilities, cards, loc, enums = sqlite2json(r'C:\Program Files\Wizards of the Coast\MTGA\MTGA_Data\Downloads\Raw\Raw_CardDatabase_cd2453dbad375992da5ce57a87044f40.mtga')

    with open("abilities.json", "w", encoding='utf-8') as f:
       dump(abilities, f, indent=2, ensure_ascii=False)
    
    with open("cards.json", "w", encoding='utf-8') as f:
        dump(cards, f, indent=2, ensure_ascii=False)

    with open("loc.json", "w", encoding='utf-8') as f:
       dump(loc, f, indent=2, ensure_ascii=False)
    
    with open("enums.json", "w", encoding='utf-8') as f:
        dump(enums, f, indent=2, ensure_ascii=False)
