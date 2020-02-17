import sys
def draw_ladder(height):
    """
    >>> draw_ladder(0)
    >>> draw_ladder(-1)
    >>> draw_ladder(1)
    #
    >>> draw_ladder(2)
     #
    ##
    >>> draw_ladder(3)
      #
     ##
    ###
    """
    if height < 1:
        return
    stair = [' ' for i in range(height)]
    fill_pos = height - 1
    while fill_pos >= 0:
        stair[fill_pos] = '#'
        print(''.join(stair))
        fill_pos -= 1
    return

if __name__ == "__main__":
    num = int(sys.argv[1])
    draw_ladder(num)