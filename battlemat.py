class Tile:
    """Tile data structure"""

    def __init__(self, loc=[0,0], tilesize=[1,1]):
        self.loc = loc
        self.tilesize = tilesize

class Battlemat:

    import sys
    
    """Combat map class"""

    def __init__(self):
        self.tokens = []
        self.items = []
        
    def __sizeof__(self):
        return object.__sizeof__(self) + \
            sum(sys.getsizeof(v) for v in self.__dict__.values())

###################################################################
#
# Input functions

    def add_token(self,token):
        if "loc" not in dir(token):
            return None

        self.tokens.append(token)
        return token
    
    def remove_token(self,token):
        if "loc" not in dir(token):
            return None
        
        self.tokens.remove(token)
    
    def add_item(self, item, loc):
        self.items.append([item,loc])

###################################################################
#
# Token manipulation functions

    def move_token(self,token,tile):
        start_loc = token.loc
        token.loc = tile
        return self.dist_ft(start_loc,tile)

###################################################################
#
# Calculation functions

    def dist_tile(self, loc1, loc2):
        x_dist = abs(loc1[0] - loc2[0])
        y_dist = abs(loc1[1] - loc2[1])

        straight_dist = abs(x_dist - y_dist)
        diag_dist = int(min(x_dist,y_dist) * 3 / 2)

        return straight_dist + diag_dist

    def dist_ft(self, loc1, loc2):
        return self.dist_tile(loc1,loc2) * 5

    def tile_rect(self, corner1, corner2):
        tile_list = []
        x1, y1 = corner1
        x2, y2 = corner2
        for x in range(x1,x2+1):
            tile_list.append([x,y1])
        for y in range(y1+1,y2):
            tile_list.append([x1,y])
            tile_list.append([x2,y])
        for x in range(x1,x2+1):
            tile_list.append([x,y2])

        return tile_list

    def tile_rect_fill(self, corner1, corner2):
        tile_list = []
        x1, y1 = corner1
        x2, y2 = corner2

        for x in range(x1, x2+1):
            for y in range(y1, y2+1):
                tile_list.append([x,y])

        return tile_list

    def threatened_tiles(self, token):
        threat_range = token.threat_range()
        min_threat, max_threat = threat_range
        min_threat //= 5
        max_threat //= 5

        corner1 = [token.loc[0] - max_threat, token.loc[1] - max_threat]
        corner2 = [token.loc[0] + token.tilesize[0] + max_threat - 1, token.loc[1] + token.tilesize[1] + max_threat - 1]

        tile_list = self.tile_rect_fill(corner1, corner2)
        token_tiles = self.token_occupy(token)

        for tile in token_tiles:
            tile_list.remove(tile)

        out_list = []

        for tile in tile_list:
            for token_tile in token_tiles:
                dist = self.dist_tile(tile, token_tile)

                if dist >= min_threat and dist <= max_threat:
                    out_list.append(tile)
                    break

        return out_list

    def threaten(self, token1, token2):
        threat_tile_list = map(tuple,self.threatened_tiles(token1))
        token_tile_list = map(tuple,self.token_occupy(token2))

        overlap = set(threat_tile_list) & set(token_tile_list)

        return len(overlap)!=0
    
    def check_threat(self, fighter, tile):
        threat = False
        for foe in self.tokens:
            if foe.side == fighter.side:
                continue
            
            if tile in self.threatened_tiles[foe]:
                threat = True
                break
        
        return threat

        # Note: current test only works for 1x1 combatants, fix in future

    def can_attack(self, token1, token2):
        if "M" in token1.weap_type() and not self.threaten(token1, token2):
            return False
        if "R" in token1.weap_type() and self.dist_ft(token1.loc,token2.loc) > token1.weap_range() * 5:
            return False
        return True

    def adjacent_tiles(self, loc, size=[1,1]):
        corner1 = [loc[0] - 1, loc[1] - 1]
        corner2 = [loc[0] + size[0], loc[1] + size[1]]

        return self.tile_rect(corner1, corner2)

    def closest_adj_tile(self, token1, token2):
        dist = 999
        out_tile = None
        for tile in self.adjacent_tiles(token2.loc):
            check_dist = self.dist_tile(tile,token1.loc)
            if check_dist < dist:
                dist = check_dist
                out_tile = tile

        return out_tile

    def token_occupy(self, token):
        corner1 = token.loc
        corner2 = [token.loc[0] + token.tilesize[0] - 1,token.loc[1] + token.tilesize[1] - 1]

        return self.tile_rect_fill(corner1, corner2)

    def token_overlap(self, token1, token2):
        tile_list1 = map(tuple,self.token_occupy(token1))
        tile_list2 = map(tuple,self.token_occupy(token2))

        overlap = set(tile_list1) & set(tile_list2)

        return len(overlap)!=0

    def closest_token_tile(self, token1, token2):
        dist = 999
        out_tile = None
        for tile in self.token_occupy(token2):
            check_dist = self.dist_tile(tile,token1.loc)
            if check_dist < dist:
                dist = check_dist
                out_tile = tile

        return out_tile


    def partial_path(self, token1, token2, move=2000, tile=True, size1=None, size2=None):
        path = []
        if not tile:
            orig = token1
            dest = token2
            token1 = Tile(orig, size1)
            token2 = Tile(dest, size2)
        tile = Tile(token1.loc,token1.tilesize)
        tile_dest = Tile(self.closest_token_tile(token1, token2))
        step = self.closest_adj_tile(tile_dest, tile)
        total_move = self.dist_ft(token1.loc, step)
        while not self.token_overlap(tile, token2) and total_move < move and len(path) < 50:
            path.append(step)
            tile.loc = step
            step = self.closest_adj_tile(tile_dest, tile)
            total_move = self.dist_ft(token1.loc, step)
        if not tile:
            del token1
            del token2
        del tile
        del tile_dest

        return path[:-1]


###################################################################
#
# Output functions

    def token_list_sorted(self):
        s = sorted(self.tokens, key=lambda token:token.loc[1])
        return sorted(s, key=lambda token:token.loc[0])

    def output(self):
        out = []

        for token in self.tokens:
            tokendata = [token.name, token.loc, token.size, token.side]
            out.append(tokendata)

        return out
