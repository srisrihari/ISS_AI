import sys; lines = open(sys.argv[1]).readlines(); lines[299] = "        \n"; lines[300] = "        return best_position\n"; open(sys.argv[1], "w").writelines(lines)
