#!/usr/bin/env python

import os, sys, datetime, json, traceback, re, signal

exiting = False

def signal_handler(signal, frame):
    global exiting
    print 'Ctrl+C'
    exiting = True
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

tmp_stats = {}

def get_str(d, k):
    v = d.get(k)
    if isinstance(v, basestring):
        v = v.encode('ascii', 'ignore')
    else:
        v = '%s' % (v,)
    return v

def parse_line(line):

    v = line.split(' - ')
    c = ' - '.join(v[3:])
    
    j = None
    try:
        j = json.loads(c)
    except ValueError:
        # skip json decode error
        return

    # print repr(j)
    # sys.exit()

    stat = j[2]
    # print stat
    
    snsid = stat[3]
    achivs = stat[4]

    # temp obj for lookup
    t = {}
    for ach in achivs:
        aid, finished, mark, step = ach
        k = "%s" % (aid,)
        t[k] = ach

    line_printed = False

    if snsid not in tmp_stats:
        tmp_stats[snsid] = None
    else:
        # compare
        #print "compare %s" % (snsid,)

        for ach in tmp_stats[snsid]:
            aid, finished, mark, step = ach
            k = "%s" % (aid,)
            if k in t:
                c_aid, c_finished, c_mark, c_step = t[k]
                if c_finished < finished or c_mark < mark or c_step < step:
                    if not line_printed:
                        print line
                        line_printed = True

                    print "miss: snsid=%s, p=%s, c=%s" % (snsid, ach, t[k])
            else:
                if not line_printed:
                    print line
                    line_printed = True
                print "lost: snsid=%s, p=%s, id=%s" % (snsid, ach, k)
 

    tmp_stats[snsid] = achivs
    


def parse_file(filename):
    fp = open(filename, 'r')
    if fp:
        for line in fp:

            if exiting:
                break

            line = line.strip()
            try:
                parse_line(line)
            except:
                err_msg = "Unexpected error: %s" % ( traceback.format_exc(), )
                print >> sys.stderr, err_msg

    else:
        print >> sys.stderr, 'open failed'


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print >> sys.stderr, 'invalid arguments'
        sys.exit()

    filename = sys.argv[1]
    
    parse_file(filename)

    print >> sys.stderr, 'end'


