#!/usr/bin/python3
import sys
""" template of counters_*.out:
0 memdefrag_defrag 0
1    memdefrag_scan 0
2    memdefrag_dest_free_pages 0
3    memdefrag_dest_anon_pages 0
4 memdefrag_dest_file_pages 0
5 memdefrag_dest_free_pages_failed 0
6 memdefrag_dest_anon_pages_failed 0
7 memdefrag_dest_file_pages_failed 0
8 memdefrag_dest_nonlru_pages_failed 0
9 memdefrag_dest_unmovable_pages_failed 0
10 memdefrag_src_compound_pages_failed 0
11 memdefrag_dst_compound_pages_failed 0
12 memdefrag_src_split_hugepages 0
13 memdefrag_dst_split_hugepages 0
(obsolete) fails
(new) out of bounds
14 Capaging failure 4K (0-order) counters:
15 INVALID_PFN:	0
16 EXCEED_MEMORY:	0
17 GUARD_PAGE:	0
PCP_PAGE: 0
OCCUPIED:	0
BUDDY_OCCUPIED:	0
WRONG_ALIGNMENT:	0
EXCEED_ZONE:	0
NOTHING_FOUND:	0
BUDDY_GUARD:	0
SUBBLOCK:	0
PAGECACHE:	0
26 NUMA:	0
Capaging failure 2M (9-order) counters:
28 INVALID_PFN:	0
EXCEED_MEMORY:	0
GUARD_PAGE:	0
PCP_PAGE: 0
OCCUPIED:	0
BUDDY_OCCUPIED:	0
WRONG_ALIGNMENT:	0
EXCEED_ZONE:	0
NOTHING_FOUND:	0
BUDDY_GUARD:	0
SUBBLOCK:	0
PAGECACHE:	0
NUMA:	0
"""

def parse_counter_file(file_name):
    f = open(file_name, 'r')
    lines = f.readlines()
    lines = [line.rstrip('\n') for line in lines]
    cap_4k_fails_start_line = 15
    cap_2m_fails_start_line = 29

    # below code is because some counters* file have one more line
    has_total_fails_line = False
    for line in lines:
        if "memdefrag_fails" in line:
            cap_4k_fails_start_line += 1
            cap_2m_fails_start_line += 1
        if "dst_out_of_bounds" in line:
            cap_4k_fails_start_line += 1
            cap_2m_fails_start_line += 1

    defrag_lines = lines[0 : cap_4k_fails_start_line-1]
    cap_4k_fails_lines = lines[cap_4k_fails_start_line : cap_4k_fails_start_line+13]
    cap_2m_fails_lines = lines[cap_2m_fails_start_line : cap_2m_fails_start_line+13]
    # defrag
    defrag_vals = [int(line.split()[1]) for line in defrag_lines]
    dst_free_tries, dst_anon_tries, dst_file_tries = defrag_vals[2:5]
    dst_free_fails, dst_anon_fails, dst_file_fails = defrag_vals[5:8]
    dst_nonlru_fails, dst_unmov_fails = defrag_vals[8:10]
    src_comp_fails, dst_comp_fails = defrag_vals[10:12]

    defrag_success = (dst_free_tries+dst_anon_tries+dst_free_tries) - \
                     (dst_free_fails+dst_anon_fails+dst_file_fails)
    defrag_fails = dst_free_fails + dst_anon_fails + dst_file_fails + \
                   dst_nonlru_fails + dst_unmov_fails + \
                   src_comp_fails + dst_comp_fails

    # calculate total 4k failures
    total_cap_4k_fails = sum([int(line.split()[1]) for line in cap_4k_fails_lines])
    # calculate total 2m failures
    total_cap_2m_fails = sum([int(line.split()[1]) for line in cap_2m_fails_lines])

    return defrag_success, defrag_fails, total_cap_4k_fails, total_cap_2m_fails


def main():
    args = sys.argv
    if len(args) != 3:
        print("Wrong number of arguments!")
        exit()
    start_file = args[1]
    end_file = args[2]
    def_succ_st, def_fails_st, cap_4k_fails_st, cap_2m_fails_st = parse_counter_file(start_file)
    def_succ_end, def_fails_end, cap_4k_fails_end, cap_2m_fails_end = parse_counter_file(end_file)
    def_succ_diff = def_succ_end - def_succ_st
    def_fails_diff = def_fails_end - def_fails_st
    cap_4k_fails_diff = cap_4k_fails_end - cap_4k_fails_st
    cap_2m_fails_diff = cap_2m_fails_end - cap_2m_fails_st
    def_fails_diff_gb = def_fails_diff*4 / (1024*1024)
    def_succ_diff_gb = def_succ_diff*4 / (1024*1024)
    cap_4k_fails_diff_gb = cap_4k_fails_diff*4 / (1024*1024)
    cap_2m_fails_diff_gb = cap_2m_fails_diff*2 / (1024)
    #print("{}, {}, {}, {}".format(def_succ_diff, def_fails_diff, cap_4k_fails_diff, cap_2m_fails_diff))
    print("Defrag successes (in 4K pages): {} ({:.4f}GB)".format(def_succ_diff, def_succ_diff_gb))
    print("Defrag failures (in 4K pages): {} ({:.4f}GB)".format(def_fails_diff, def_fails_diff_gb))
    print("Cap 4k fails: {} ({:.4f}GB)".format(cap_4k_fails_diff, cap_4k_fails_diff_gb))
    print("Cap 2m fails: {} ({:.4f}GB)".format(cap_2m_fails_diff, cap_2m_fails_diff_gb))

if __name__ == "__main__":
    main()
