COLORMAP = {
    "R": "Red",
    "W": "White",
    "B": "Black",
    "U": "Blue",
    "G": "Green"
}

class Card(object):

    def __init__(self, name="", pretty_name="", kana_name="", cost=None, color_identity=None, card_type="", sub_types="", super_types="",
                 abilities=None, set_id="", rarity="", collectible=True, set_number=-1, mtga_id=-1,
                 is_token=False, is_secondary_card=False, is_rebalanced=False, is_digital_only=False):
        self.name = name
        self.set = set_id
        self.pretty_name = pretty_name
        self.kana_name = kana_name
        if cost is None:
            cost = []
        self.cost = cost
        if color_identity is None:
            color_identity = []
        self.color_identity = color_identity
        self.card_type = card_type
        self.sub_types = sub_types
        self.super_types = super_types
        self.set_number = set_number
        self.mtga_id = mtga_id
        self.rarity = rarity
        self.collectible = collectible
        if abilities is None:
            abilities = []
        self.abilities = abilities
        self.is_token = is_token
        self.is_secondary_card = is_secondary_card
        self.is_rebalanced = is_rebalanced
        self.is_digital_only = is_digital_only

    @property
    def abilities_decoded(self):
        from ..set_data import all_mtga_abilities
        return {ability_id: all_mtga_abilities[ability_id] for ability_id in self.abilities}


    @property
    def colors(self):
        colors = []
        for color_key in COLORMAP.keys():
            if color_key in self.cost or color_key in self.color_identity:
                colors.append(COLORMAP[color_key])
        if not colors:
            if self.card_type == "Basic Land":
                if "Plains" in self.pretty_name:
                    colors = ["White"]
                if "Swamp" in self.pretty_name:
                    colors = ["Black"]
                if "Forest" in self.pretty_name:
                    colors = ["Green"]
                if "Mountain" in self.pretty_name:
                    colors = ["Red"]
                if "Island" in self.pretty_name:
                    colors = ["Blue"]
            if not colors:
                colors = ["Colorless"]
        return colors

    @property
    def cmc(self):
        'gets converted mana cost for a card'
        cmc = 0
        for symbol in self.cost:
            if symbol.isdigit():
                cmc += int(symbol)
            elif symbol == "X":
                continue
            else:
                cmc += 1
        return cmc

    def to_serializable(self):
        return {
            "name": self.name,
            "set": self.set,
            "colors": self.colors,
            "pretty_name": self.pretty_name,
            "kana_name": self.kana_name,
            "cost": self.cost,
            "color_identity": self.color_identity,
            "card_type": self.card_type,
            "sub_types": self.sub_types,
            "super_types": self.super_types,
            "rarity": self.rarity,
            "set_number": self.set_number,
            "mtga_id": self.mtga_id
        }
    
    @property
    def is_creature_card(self):
        if "クリーチャー" in self.card_type or "Creature" in self.card_type:
            return True
        else:
            return False

    @property
    def is_land_card(self):
        if "土地" in self.card_type or "Land" in self.card_type:
            return True
        else:
            return False

    @property
    def is_noncreature_spell_card(self):
        if not self.is_creature_card and not self.is_land_card:
            return True
        else:
            return False

    @property
    def is_basic(self):
        if "基本" in self.super_types or "Basic" in self.super_types:
            return True
        else:
            return False

    @classmethod
    def from_dict(cls, obj):
        from ..set_data import all_mtga_cards
        try:
            return all_mtga_cards.find_one(obj["mtga_id"])
        except ValueError:
            new_unknown_card = cls("unknown_{}".format(obj["mtga_id"]), "{}: Unknown MTGA ID".format(obj["mtga_id"]), [], [], "unknown", "unknown", "unknown", -1, obj["mtga_id"])
            all_mtga_cards.cards.append(new_unknown_card)
            return new_unknown_card

    def __repr__(self):
        return "<Card: '{}' {} {} {}>".format(self.pretty_name, self.colors, self.set, self.mtga_id)

    def __str__(self):
        return self.__repr__()


class GameCard(Card):

    def __init__(self, name, pretty_name, kana_name, cost, color_identity, card_type, sub_types, super_types, set_id, rarity, set_number, mtga_id, owner_seat_id, game_id=-1):
        super().__init__(name, pretty_name, kana_name, cost, color_identity, card_type, sub_types, super_types, set_id, rarity, set_number, mtga_id)
        self.game_id = game_id
        self.previous_iids = []
        self.owner_seat_id = owner_seat_id

    def to_serializable(self):
        serial = super(GameCard, self).to_serializable()
        serial["iid"] = self.game_id
        serial["owner_seat_id"] = self.owner_seat_id
        return serial

    def __repr__(self):
        if self.mtga_id != -1:
            return "<GameCard: {} {} iid={}>".format(self.name, self.mtga_id, self.game_id)
        else:
            return "<UnknownCard: iid={}>".format(self.game_id)

    def transform_to(self, card_id):
        from ..set_data import all_mtga_cards
        new_card = all_mtga_cards.find_one(card_id)
        self.name = new_card.name
        self.pretty_name = new_card.pretty_name
        self.kana_name = new_card.kana_name
        self.cost = new_card.cost
        self.card_type = new_card.card_type
        self.sub_types = new_card.sub_types
        self.super_types = new_card.super_types
        self.set = new_card.set
        self.set_number = new_card.set_number
        self.mtga_id = new_card.mtga_id
